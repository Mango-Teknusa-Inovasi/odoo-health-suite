# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HealthPrescriptionLine(models.Model):
    _name = 'health.prescription.line'
    _description = 'Prescription Standard Medicine Line'
    _order = 'id asc'

    prescription_id = fields.Many2one('health.prescription', string='Resep', required=True, ondelete='cascade', index=True)
    product_id = fields.Many2one('product.product', string='Nama Obat / Alkes', required=True, index=True)
    dosage_form = fields.Selection(related='product_id.health_dosage_form', string='Bentuk Sediaan', readonly=True)
    quantity = fields.Float(string='Jumlah / Qty', required=True, default=1.0)
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id', string='Satuan', readonly=True)

    dosage_instruction = fields.Char(string='Aturan Pakai (Signa)', required=True, default='3 x 1 tablet sesudah makan')
    route = fields.Selection([
        ('oral', 'Obat Dalam (Oral)'),
        ('topical', 'Obat Luar (Topikal/Salep)'),
        ('injection', 'Injeksi / Infus'),
        ('inhalation', 'Inhalasi'),
        ('eye_drop', 'Tetes Mata'),
        ('ear_drop', 'Tetes Telinga'),
        ('other', 'Lainnya'),
    ], string='Rute Pemberian', default='oral', required=True)

    days_supply = fields.Integer(string='Durasi (Hari)', default=3)
    special_notes = fields.Char(string='Catatan Tambahan', help='cth. Habiskan (Antibiotik), Sebelum Makan')
    price_unit = fields.Float(related='product_id.list_price', string='Harga Satuan (Rp)', readonly=True)
    subtotal = fields.Float(string='Subtotal (Rp)', compute='_compute_subtotal', store=True)
    lot_id = fields.Many2one('stock.lot', string='No. Batch / Lot FEFO', domain="[('product_id', '=', product_id)]")

    @api.depends('quantity', 'product_id.list_price')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = (rec.quantity or 0.0) * (rec.product_id.list_price or 0.0)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and self.product_id.health_standard_signa:
            self.dosage_instruction = self.product_id.health_standard_signa
