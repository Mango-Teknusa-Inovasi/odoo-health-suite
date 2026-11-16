# -*- coding: utf-8 -*-
from odoo import models, fields

class HealthSpecialty(models.Model):
    _name = 'health.specialty'
    _description = 'Medical Specialty'
    _order = 'name'

    name = fields.Char(string='Specialty Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True, index=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'The specialty code must be unique!')
    ]
