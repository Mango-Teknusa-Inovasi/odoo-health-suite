# -*- coding: utf-8 -*-
from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    health_prescription_id = fields.Many2one(
        'health.prescription',
        string='Rujukan Resep Dokter',
        readonly=True,
        copy=False,
        index=True
    )
