# -*- coding: utf-8 -*-
from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    health_billing_id = fields.Many2one(
        'health.billing',
        string='Rujukan Tagihan Rumah Sakit',
        readonly=True,
        copy=False,
        index=True
    )
