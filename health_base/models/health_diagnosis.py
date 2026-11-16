# -*- coding: utf-8 -*-
from odoo import models, fields

class HealthDiagnosis(models.Model):
    _name = 'health.diagnosis'
    _description = 'ICD-10 Diagnostic Catalog'
    _order = 'code'
    _rec_name = 'display_name'

    code = fields.Char(string='ICD-10 Code', required=True, index=True)
    name = fields.Char(string='Diagnosis Name', required=True, index=True)
    category = fields.Char(string='Category / Chapter', index=True)
    description = fields.Text(string='Clinical Description')
    is_contagious = fields.Boolean(string='Penyakit Menular', default=False)
    active = fields.Boolean(default=True)

    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'The ICD-10 code must be unique!')
    ]

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"[{rec.code}] {rec.name}" if rec.code and rec.name else (rec.code or rec.name or '')
