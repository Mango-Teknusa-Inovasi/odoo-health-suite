# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HealthPrescriptionCompound(models.Model):
    _name = 'health.prescription.compound'
    _description = 'Compounded Medicine (Puyer / Kapsul / Salep)'
    _order = 'id asc'

    prescription_id = fields.Many2one('health.prescription', string='Resep', required=True, ondelete='cascade', index=True)
    name = fields.Char(string='Nama Racikan', required=True, default='Racikan 1 (Puyer Batuk Pilek)')
    compound_type = fields.Selection([
        ('pulveres', 'Puyer (Serbuk Bagi)'),
        ('capsule', 'Kapsul Racikan'),
        ('syrup', 'Sirup Campuran'),
        ('ointment', 'Salep / Krim Racikan'),
    ], string='Metode Racik', default='pulveres', required=True)

    quantity = fields.Integer(string='Jumlah Bungkus / Kapsul / Pot', required=True, default=10)
    dosage_instruction = fields.Char(string='Aturan Pakai (Signa)', required=True, default='3 x 1 bungkus sesudah makan')
    route = fields.Selection([
        ('oral', 'Obat Dalam (Oral)'),
        ('topical', 'Obat Luar (Topikal)'),
    ], string='Rute Pemberian', default='oral', required=True)

    embalage_fee = fields.Float(string='Biaya Embalase (Rp)', default=500.0, help='Biaya cangkang kapsul, kertas puyer, pot salep')
    tuslah_fee = fields.Float(string='Jasa Tuslah Racik (Rp)', default=5000.0, help='Jasa profesional peracikan farmasi')

    ingredient_ids = fields.One2many('health.prescription.compound.line', 'compound_id', string='Komposisi Bahan Aktif')
    subtotal_ingredients = fields.Float(string='Total Bahan Baku (Rp)', compute='_compute_totals', store=True)
    total_price = fields.Float(string='Total Harga Racikan (Rp)', compute='_compute_totals', store=True)

    @api.depends('ingredient_ids.subtotal', 'embalage_fee', 'tuslah_fee', 'quantity')
    def _compute_totals(self):
        for rec in self:
            ingredients_sum = sum(rec.ingredient_ids.mapped('subtotal'))
            rec.subtotal_ingredients = ingredients_sum
            # Total = bahan baku + (embalase * jumlah) + tuslah
            total_embalage = rec.embalage_fee * (rec.quantity or 1)
            rec.total_price = ingredients_sum + total_embalage + rec.tuslah_fee


class HealthPrescriptionCompoundLine(models.Model):
    _name = 'health.prescription.compound.line'
    _description = 'Compounded Medicine Active Ingredient Line'
    _order = 'id asc'

    compound_id = fields.Many2one('health.prescription.compound', string='Racikan', required=True, ondelete='cascade', index=True)
    product_id = fields.Many2one('product.product', string='Bahan Obat Aktif', required=True, index=True)
    dosage_per_unit = fields.Float(string='Dosis per Bungkus (mg)', help='Kandungan miligram yang diminta dokter per bungkus puyer/kapsul')
    total_quantity = fields.Float(string='Total Tablet / Satuan Digunakan', required=True, default=1.0,
                                  help='Jumlah tablet/satuan utuh yang digerus/diambil dari gudang obat')
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id', string='Satuan', readonly=True)
    price_unit = fields.Float(related='product_id.list_price', string='Harga Satuan (Rp)', readonly=True)
    subtotal = fields.Float(string='Subtotal (Rp)', compute='_compute_subtotal', store=True)
    lot_id = fields.Many2one('stock.lot', string='No. Batch / Lot FEFO', domain="[('product_id', '=', product_id)]")

    @api.depends('total_quantity', 'product_id.list_price')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = (rec.total_quantity or 0.0) * (rec.product_id.list_price or 0.0)
