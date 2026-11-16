# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HealthPhysicianFee(models.Model):
    _name = 'health.physician.fee'
    _description = 'Doctor Remuneration & PPh 21 Withholding Ledger'
    _order = 'date desc, id desc'

    name = fields.Char(string='No. Remunerasi', required=True, copy=False, readonly=True, default='/')
    physician_id = fields.Many2one('health.physician', string='Dokter', required=True, index=True)
    billing_id = fields.Many2one('health.billing', string='Rujukan Billing Pasien', index=True, ondelete='cascade')
    appointment_id = fields.Many2one('health.appointment', string='Kunjungan Rawat Jalan', index=True)
    patient_id = fields.Many2one('health.patient', string='Pasien', index=True)
    date = fields.Date(string='Tanggal Tindakan / Pelayanan', default=fields.Date.context_today, required=True)
    service_name = fields.Char(string='Uraian Layanan Medis', required=True)

    gross_amount = fields.Float(string='Jasa Medis Bruto (Rp)', required=True, default=0.0)
    pph21_rate = fields.Float(string='Tarif Efektif PPh 21 (%)', default=2.5,
                              help='Sesuai ketentuan PPh 21 Tenaga Ahli Dokter (50% DPP x 5% tarif = 2.5% efektif bruto)')
    pph21_amount = fields.Float(string='Potongan Pajak PPh 21 (Rp)', compute='_compute_net_amount', store=True)
    net_amount = fields.Float(string='Jasa Medis Bersih / Hak Dokter (Rp)', compute='_compute_net_amount', store=True)

    state = fields.Selection([
        ('draft', 'Tercatat (Belum Disetujui)'),
        ('approved', 'Disetujui untuk Payout'),
        ('paid', 'Telah Dibayarkan / Settlement'),
        ('cancelled', 'Dibatalkan'),
    ], string='Status Remunerasi', default='draft', index=True)

    vendor_bill_id = fields.Many2one('account.move', string='Faktur Hutang Dokter (Vendor Bill)', readonly=True, copy=False)
    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)

    @api.depends('gross_amount', 'pph21_rate')
    def _compute_net_amount(self):
        for rec in self:
            tax = (rec.gross_amount * (rec.pph21_rate / 100.0)) if rec.pph21_rate else 0.0
            rec.pph21_amount = tax
            rec.net_amount = rec.gross_amount - tax

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('health.physician.fee') or '/'
        return super(HealthPhysicianFee, self).create(vals_list)

    def action_approve(self):
        for rec in self:
            rec.state = 'approved'

    def action_generate_vendor_bill(self):
        """Generates grouped Vendor Bill (account.move) for approved physician remuneration records."""
        for rec in self:
            if rec.state != 'approved':
                raise UserError(_("Remunerasi harus disetujui (Approved) terlebih dahulu sebelum membuat Vendor Bill!"))
            if rec.vendor_bill_id:
                raise UserError(_("Vendor Bill sudah pernah dibuat untuk transaksi ini (%s)!") % rec.vendor_bill_id.name)

            partner = self.env['res.partner'].search([('name', '=', rec.physician_id.name)], limit=1)
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': rec.physician_id.name,
                    'supplier_rank': 1,
                })

            invoice_vals = {
                'move_type': 'in_invoice',
                'partner_id': partner.id,
                'invoice_date': fields.Date.context_today(self),
                'ref': f"Remunerasi Dokter: {rec.name} ({rec.service_name})",
                'invoice_line_ids': [
                    (0, 0, {
                        'name': f"Jasa Medis: {rec.service_name} (Pasien: {rec.patient_id.name or '-'})",
                        'price_unit': rec.gross_amount,
                        'quantity': 1.0,
                    }),
                    (0, 0, {
                        'name': f"Potongan PPh 21 Tenaga Ahli Dokter ({rec.pph21_rate}%)",
                        'price_unit': -rec.pph21_amount,
                        'quantity': 1.0,
                    }) if rec.pph21_amount > 0 else None
                ]
            }
            # Remove None lines
            invoice_vals['invoice_line_ids'] = [line for line in invoice_vals['invoice_line_ids'] if line]

            bill = self.env['account.move'].create(invoice_vals)
            rec.vendor_bill_id = bill.id
            rec.state = 'paid'

        return True
