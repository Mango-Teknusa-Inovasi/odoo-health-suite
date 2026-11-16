# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class HealthPrescription(models.Model):
    _name = 'health.prescription'
    _description = 'Electronic Prescription & Dispensary'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string='No. Resep', required=True, copy=False, readonly=True, default='/')
    date = fields.Datetime(string='Waktu Peresepan', required=True, default=fields.Datetime.now, tracking=True)

    patient_id = fields.Many2one('health.patient', string='Pasien', required=True, tracking=True, index=True)
    medical_record_no = fields.Char(related='patient_id.medical_record_no', string='No. Rekam Medis', store=True)
    physician_id = fields.Many2one('health.physician', string='Dokter Penulis Resep', required=True, tracking=True, index=True)
    appointment_id = fields.Many2one('health.appointment', string='Kunjungan Rawat Jalan', index=True)
    soap_id = fields.Many2one('health.emr.soap', string='Catatan Klinis SOAP', index=True)

    state = fields.Selection([
        ('draft', 'Resep Baru (Dokter)'),
        ('reviewed', 'Telaah Farmasi Lolos'),
        ('dispensed', 'Disiapkan & Dikemas'),
        ('delivered', 'Diserahkan ke Pasien'),
        ('cancelled', 'Dibatalkan'),
    ], string='Status Resep', default='draft', tracking=True, index=True)

    # Permenkes 73/2016 3-Layer Clinical Audit
    pharmacist_id = fields.Many2one('res.users', string='Apoteker Penelaah', tracking=True)
    review_administrative = fields.Boolean(
        string='Kajian Administratif',
        help='Kejelasan nama dokter, SIP, paraf, tanggal peresepan, nama & umur/berat badan pasien.'
    )
    review_pharmaceutical = fields.Boolean(
        string='Kajian Farmasetik',
        help='Bentuk sediaan, dosis, potensi inkompatibilitas stabilitas obat.'
    )
    review_clinical = fields.Boolean(
        string='Kajian Klinis',
        help='Ketepatan indikasi, duplikasi terapi, alergi, dan potensi interaksi obat berbahaya.'
    )
    pharmacist_notes = fields.Text(string='Catatan Konseling Apoteker')

    line_ids = fields.One2many('health.prescription.line', 'prescription_id', string='Daftar Obat Jadi')
    compound_ids = fields.One2many('health.prescription.compound', 'prescription_id', string='Daftar Obat Racikan')

    amount_total = fields.Float(string='Total Biaya Obat (Rp)', compute='_compute_amount_total', store=True)
    picking_id = fields.Many2one('stock.picking', string='Dokumen Pengeluaran Obat (Picking)', copy=False, readonly=True)
    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)

    _sql_constraints = [
        ('health_prescription_name_unique', 'unique(name, company_id)', 'Nomor resep harus unik per fasilitas kesehatan!')
    ]

    @api.depends('line_ids.subtotal', 'compound_ids.total_price')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped('subtotal')) + sum(rec.compound_ids.mapped('total_price'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('health.prescription') or '/'
        return super(HealthPrescription, self).create(vals_list)

    def action_verify_review(self):
        """Verifies Permenkes 73/2016 3-layer clinical review unless Solo Fast-Track mode is enabled."""
        ICP = self.env['ir.config_parameter'].sudo()
        fast_track = ICP.get_param('health_pharmacy.fast_track_review', default=False)

        for rec in self:
            if not rec.line_ids and not rec.compound_ids:
                raise UserError(_("Resep tidak memiliki daftar obat maupun racikan!"))

            if not fast_track:
                missing = []
                if not rec.review_administrative:
                    missing.append(_("Kajian Administratif"))
                if not rec.review_pharmaceutical:
                    missing.append(_("Kajian Farmasetik"))
                if not rec.review_clinical:
                    missing.append(_("Kajian Klinis"))

                if missing:
                    raise UserError(_("Gagal verifikasi resep! Sesuai Permenkes 73/2016, apoteker wajib mencentang: %s.") % ", ".join(missing))

            rec.pharmacist_id = self.env.user
            rec.state = 'reviewed'

    def action_dispense(self):
        """Prepares and packages medicines, allocating stock picking with FEFO lots."""
        for rec in self:
            if rec.state != 'reviewed':
                raise UserError(_("Resep harus lolos telaah farmasi terlebih dahulu sebelum disiapkan!"))

            # Create stock.picking if warehouse stock module is installed and locations exist
            try:
                warehouse = self.env['stock.warehouse'].search([('company_id', '=', rec.company_id.id)], limit=1)
                picking_type = warehouse.out_type_id or self.env['stock.picking.type'].search([('code', '=', 'outgoing')], limit=1)
                partner = rec.patient_id.partner_id or self.env['res.partner'].search([('name', '=', rec.patient_id.name)], limit=1)
                if not partner:
                    partner = self.env['res.partner'].create({'name': rec.patient_id.name})
                    rec.patient_id.partner_id = partner.id

                if picking_type and warehouse:
                    move_lines = []
                    # Standard medicine lines
                    for line in rec.line_ids:
                        move_lines.append((0, 0, {
                            'name': f"Resep {rec.name}: {line.product_id.name}",
                            'product_id': line.product_id.id,
                            'product_uom_qty': line.quantity,
                            'product_uom': line.uom_id.id or line.product_id.uom_id.id,
                            'location_id': picking_type.default_location_src_id.id or warehouse.lot_stock_id.id,
                            'location_dest_id': partner.property_stock_customer.id or self.env.ref('stock.stock_location_customers').id,
                        }))

                    # Compounded active ingredients lines
                    for comp in rec.compound_ids:
                        for ing in comp.ingredient_ids:
                            move_lines.append((0, 0, {
                                'name': f"Racikan {comp.name} ({rec.name}): {ing.product_id.name}",
                                'product_id': ing.product_id.id,
                                'product_uom_qty': ing.total_quantity,
                                'product_uom': ing.uom_id.id or ing.product_id.uom_id.id,
                                'location_id': picking_type.default_location_src_id.id or warehouse.lot_stock_id.id,
                                'location_dest_id': partner.property_stock_customer.id or self.env.ref('stock.stock_location_customers').id,
                            }))

                    if move_lines:
                        picking = self.env['stock.picking'].create({
                            'picking_type_id': picking_type.id,
                            'partner_id': partner.id,
                            'origin': rec.name,
                            'health_prescription_id': rec.id,
                            'location_id': picking_type.default_location_src_id.id or warehouse.lot_stock_id.id,
                            'location_dest_id': partner.property_stock_customer.id or self.env.ref('stock.stock_location_customers').id,
                            'move_ids_without_package': move_lines,
                        })
                        picking.action_confirm()
                        picking.action_assign() # Auto reserves stock with FEFO
                        rec.picking_id = picking.id
            except Exception as e:
                # Fallback gracefully if inventory rules not yet configured
                pass

            rec.state = 'dispensed'

    def action_deliver(self):
        """Hands over medicines to patient and marks delivery complete."""
        for rec in self:
            if rec.picking_id and rec.picking_id.state not in ['done', 'cancel']:
                try:
                    rec.picking_id.button_validate()
                except Exception:
                    pass
            rec.state = 'delivered'

    def action_cancel(self):
        for rec in self:
            if rec.picking_id and rec.picking_id.state != 'done':
                try:
                    rec.picking_id.action_cancel()
                except Exception:
                    pass
            rec.state = 'cancelled'
