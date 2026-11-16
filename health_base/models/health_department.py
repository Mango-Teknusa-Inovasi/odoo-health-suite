# -*- coding: utf-8 -*-
from odoo import models, fields

class HealthDepartment(models.Model):
    _name = 'health.department'
    _description = 'Healthcare Department / Polyclinic'
    _order = 'sequence, name'

    name = fields.Char(string='Department / Clinic Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True, index=True)
    sequence = fields.Integer(string='Sequence', default=10)
    service_type = fields.Selection([
        ('outpatient', 'Rawat Jalan / Poliklinik'),
        ('inpatient', 'Rawat Inap / Bangsal'),
        ('emergency', 'Gawat Darurat / IGD'),
        ('pharmacy', 'Farmasi / Apotek'),
        ('laboratory', 'Laboratorium'),
        ('radiology', 'Radiologi'),
        ('administration', 'Administrasi / Admisi'),
    ], string='Service Type', required=True, default='outpatient')

    default_registration_fee = fields.Monetary(string='Default Registration Fee', currency_field='currency_id', default=0.0)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    # National Regulatory Mapping
    bpjs_poli_code = fields.Char(string='BPJS Poli Code', help='Kode poli mapping BPJS PCare / VClaim')
    satusehat_location_id = fields.Char(string='SatuSehat Location ID', help='UUID Location FHIR Kemenkes SatuSehat')

    _sql_constraints = [
        ('code_company_unique', 'unique(code, company_id)', 'Department code must be unique per healthcare facility!')
    ]
