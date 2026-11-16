# -*- coding: utf-8 -*-
from odoo import models, fields

class HealthProcedure(models.Model):
    _name = 'health.procedure'
    _description = 'ICD-9 CM Procedure Catalog'
    _order = 'code'
    _rec_name = 'display_name'

    code = fields.Char(string='ICD-9 CM Code', required=True, index=True)
    name = fields.Char(string='Procedure Name', required=True, index=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)

    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'The ICD-9 CM code must be unique!')
    ]

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"[{rec.code}] {rec.name}" if rec.code and rec.name else (rec.code or rec.name or '')
