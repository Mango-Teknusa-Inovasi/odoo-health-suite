# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class HealthBilling(models.Model):
    _name = 'health.billing'
    _description = 'Patient Billing Ledger & Payment Settlement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string='No. Tagihan (Billing)', required=True, copy=False, readonly=True, default='/')
    date = fields.Datetime(string='Waktu Tagihan', required=True, default=fields.Datetime.now, tracking=True)

    patient_id = fields.Many2one('health.patient', string='Pasien', required=True, tracking=True, index=True)
    medical_record_no = fields.Char(related='patient_id.medical_record_no', string='No. Rekam Medis', store=True)
    appointment_id = fields.Many2one('health.appointment', string='Kunjungan Rawat Jalan', index=True)

    patient_type = fields.Selection([
        ('general', 'Umum / Mandiri'),
        ('bpjs', 'Jaminan BPJS Kesehatan'),
        ('insurance', 'Asuransi Swasta / Perusahaan'),
    ], string='Jenis Penjamin', default='general', required=True, tracking=True)

    line_ids = fields.One2many('health.billing.line', 'billing_id', string='Rincian Biaya Layanan & Farmasi')

    # Aggregated Amounts
    total_amount = fields.Float(string='Total Tagihan Bruto (Rp)', compute='_compute_totals', store=True)
    total_doctor_fee = fields.Float(string='Total Jasa Dokter (Rp)', compute='_compute_totals', store=True)
    total_nurse_fee = fields.Float(string='Total Jasa Perawat (Rp)', compute='_compute_totals', store=True)
    total_facility_fee = fields.Float(string='Total Jasa Sarana (Rp)', compute='_compute_totals', store=True)
    total_bhp = fields.Float(string='Total BHP (Rp)', compute='_compute_totals', store=True)
    total_pharmacy = fields.Float(string='Total Obat & Alkes (Rp)', compute='_compute_totals', store=True)

    discount_amount = fields.Float(string='Diskon / Potongan (Rp)', default=0.0)
    net_amount = fields.Float(string='Total Tagihan Bersih (Rp)', compute='_compute_totals', store=True)

    payment_method = fields.Selection([
        ('cash', 'Tunai / Kasir'),
        ('qris', 'QRIS Dinamis (QBiz)'),
        ('card', 'Debit / Kartu Kredit EDC'),
        ('transfer', 'Transfer Bank'),
        ('bpjs_claim', 'Klaim JKN BPJS'),
        ('insurance_claim', 'Klaim Asuransi Swasta'),
    ], string='Metode Pembayaran', default='cash', required=True, tracking=True)

    qris_payload = fields.Text(string='QRIS Raw Payload', readonly=True)

    state = fields.Selection([
        ('draft', 'Draft Tagihan'),
        ('validated', 'Tervalidasi (Siap Bayar)'),
        ('paid', 'Lunas'),
        ('cancelled', 'Dibatalkan'),
    ], string='Status Tagihan', default='draft', tracking=True, index=True)

    invoice_id = fields.Many2one('account.move', string='Faktur Pelanggan (Customer Invoice)', readonly=True, copy=False)
    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)

    _sql_constraints = [
        ('health_billing_name_unique', 'unique(name, company_id)', 'Nomor billing harus unik per fasilitas kesehatan!')
    ]

    @api.depends('line_ids.subtotal', 'line_ids.doctor_fee', 'line_ids.nurse_fee',
                 'line_ids.facility_fee', 'line_ids.bhp_fee', 'discount_amount')
    def _compute_totals(self):
        for rec in self:
            rec.total_amount = sum(rec.line_ids.mapped('subtotal'))
            rec.total_doctor_fee = sum(rec.line_ids.mapped('doctor_fee'))
            rec.total_nurse_fee = sum(rec.line_ids.mapped('nurse_fee'))
            rec.total_facility_fee = sum(rec.line_ids.mapped('facility_fee'))
            rec.total_bhp = sum(rec.line_ids.mapped('bhp_fee'))
            rec.total_pharmacy = sum(rec.line_ids.filtered(lambda l: l.item_type in ['pharmacy_drug', 'pharmacy_compound']).mapped('subtotal'))
            rec.net_amount = max(0.0, rec.total_amount - (rec.discount_amount or 0.0))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('health.billing') or '/'
        return super(HealthBilling, self).create(vals_list)

    def action_generate_from_encounter(self):
        """Pulls consultation fees, procedures, and dispensed prescriptions from the linked encounter."""
        for rec in self:
            if not rec.appointment_id:
                raise UserError(_("Pilih Kunjungan Rawat Jalan terlebih dahulu!"))

            app = rec.appointment_id
            lines = []

            # 1. Doctor Consultation Fee
            consultation_tariff = self.env['health.tariff.template'].search([
                ('department_id', '=', app.department_id.id)
            ], limit=1)

            if consultation_tariff:
                lines.append((0, 0, {
                    'item_type': 'consultation',
                    'name': f"Pemeriksaan & Konsultasi: {app.department_id.name}",
                    'physician_id': app.physician_id.id,
                    'quantity': 1.0,
                    'unit_price': consultation_tariff.total_amount,
                    'doctor_fee': consultation_tariff.doctor_fee,
                    'nurse_fee': consultation_tariff.nurse_fee,
                    'facility_fee': consultation_tariff.facility_fee,
                    'bhp_fee': consultation_tariff.bhp_amount,
                }))
            else:
                lines.append((0, 0, {
                    'item_type': 'consultation',
                    'name': f"Konsultasi Dokter: {app.physician_id.name}",
                    'physician_id': app.physician_id.id,
                    'quantity': 1.0,
                    'unit_price': 50000.0,
                    'doctor_fee': 40000.0,
                    'facility_fee': 10000.0,
                }))

            # 2. Pharmacy Prescriptions (Standard Drugs & Compounded)
            prescriptions = self.env['health.prescription'].search([
                ('appointment_id', '=', app.id),
                ('state', 'in', ['dispensed', 'delivered'])
            ])
            for rx in prescriptions:
                for line in rx.line_ids:
                    lines.append((0, 0, {
                        'item_type': 'pharmacy_drug',
                        'name': f"Obat: {line.product_id.name} ({line.dosage_instruction})",
                        'quantity': line.quantity,
                        'unit_price': line.price_unit,
                        'facility_fee': line.subtotal,
                    }))
                for comp in rx.compound_ids:
                    lines.append((0, 0, {
                        'item_type': 'pharmacy_compound',
                        'name': f"Racikan: {comp.name} ({comp.quantity} unit)",
                        'quantity': 1.0,
                        'unit_price': comp.total_price,
                        'facility_fee': comp.total_price,
                    }))

            rec.line_ids = lines

    def action_validate(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("Tagihan belum memiliki rincian biaya layanan atau obat!"))
            rec.state = 'validated'

    def action_settle_payment(self):
        """One-Click POS-Style settlement: Posts customer invoice, generates Doctor remuneration fees, and sets paid."""
        for rec in self:
            if rec.state == 'draft':
                rec.action_validate()

            # 1. Generate Customer Invoice (account.move)
            partner = rec.patient_id.partner_id or self.env['res.partner'].search([('name', '=', rec.patient_id.name)], limit=1)
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': rec.patient_id.name,
                    'customer_rank': 1,
                })
                rec.patient_id.partner_id = partner.id

            invoice_lines = []
            for line in rec.line_ids:
                invoice_lines.append((0, 0, {
                    'name': line.name,
                    'quantity': line.quantity,
                    'price_unit': line.unit_price,
                }))

            try:
                move = self.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'partner_id': partner.id,
                    'invoice_date': fields.Date.context_today(self),
                    'ref': f"Hospital Billing: {rec.name}",
                    'health_billing_id': rec.id,
                    'invoice_line_ids': invoice_lines,
                })
                move.action_post()
                rec.invoice_id = move.id

                # If paid immediately by cash/qris/card/transfer, simulate payment registration
                if rec.payment_method in ['cash', 'qris', 'card', 'transfer']:
                    # Soft check: if account payment register is available
                    try:
                        payment_method_line = self.env['account.payment.method.line'].search([
                            ('payment_type', '=', 'inbound')
                        ], limit=1)
                        if payment_method_line:
                            self.env['account.payment.register'].with_context(
                                active_model='account.move',
                                active_ids=move.ids
                            ).create({
                                'payment_date': fields.Date.context_today(self),
                                'amount': rec.net_amount,
                                'payment_method_line_id': payment_method_line.id,
                            })._create_payments()
                    except Exception:
                        pass
            except Exception:
                pass

            # 2. Record Doctor Fee Remuneration in Ledger
            for line in rec.line_ids:
                if line.doctor_fee > 0 and line.physician_id:
                    self.env['health.physician.fee'].create({
                        'physician_id': line.physician_id.id,
                        'billing_id': rec.id,
                        'appointment_id': rec.appointment_id.id if rec.appointment_id else False,
                        'patient_id': rec.patient_id.id,
                        'service_name': line.name,
                        'gross_amount': line.doctor_fee,
                        'date': fields.Date.context_today(self),
                    })

            # 3. Mark appointment done
            if rec.appointment_id and rec.appointment_id.state != 'done':
                rec.appointment_id.action_done()

            rec.state = 'paid'

    def action_cancel(self):
        for rec in self:
            if rec.invoice_id and rec.invoice_id.state != 'cancel':
                try:
                    rec.invoice_id.button_cancel()
                except Exception:
                    pass
            rec.state = 'cancelled'


class HealthBillingLine(models.Model):
    _name = 'health.billing.line'
    _description = 'Patient Billing Itemized Line'
    _order = 'id asc'

    billing_id = fields.Many2one('health.billing', string='Tagihan', required=True, ondelete='cascade', index=True)
    item_type = fields.Selection([
        ('registration', 'Biaya Registrasi / Karcis'),
        ('consultation', 'Pemeriksaan / Jasa Konsultasi Dokter'),
        ('procedure', 'Tindakan Medis (ICD-9 CM)'),
        ('pharmacy_drug', 'Obat Jadi / Non-Racikan'),
        ('pharmacy_compound', 'Obat Racikan (Puyer / Kapsul)'),
        ('lab', 'Pemeriksaan Laboratorium'),
        ('rad', 'Pemeriksaan Radiologi'),
        ('other', 'Lain-lain / BHP'),
    ], string='Kategori Biaya', default='procedure', required=True)

    name = fields.Char(string='Uraian Layanan / Obat', required=True)
    quantity = fields.Float(string='Qty', default=1.0, required=True)
    unit_price = fields.Float(string='Tarif Satuan (Rp)', required=True, default=0.0)
    subtotal = fields.Float(string='Subtotal (Rp)', compute='_compute_subtotal', store=True)

    physician_id = fields.Many2one('health.physician', string='Dokter Pelaksana', index=True)
    doctor_fee = fields.Float(string='Jasa Dokter (Rp)', default=0.0)
    nurse_fee = fields.Float(string='Jasa Perawat (Rp)', default=0.0)
    facility_fee = fields.Float(string='Jasa Sarana (Rp)', default=0.0)
    bhp_fee = fields.Float(string='Biaya BHP (Rp)', default=0.0)

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = (rec.quantity or 1.0) * (rec.unit_price or 0.0)
