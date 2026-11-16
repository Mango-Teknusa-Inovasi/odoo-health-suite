# -*- coding: utf-8 -*-
from odoo import models, fields, api

class HealthPhysician(models.Model):
    _name = 'health.physician'
    _description = 'Healthcare Physician / Doctor'
    _inherits = {'res.partner': 'partner_id'}
    _order = 'name'

    partner_id = fields.Many2one('res.partner', string='Contact Profile', required=True, ondelete='cascade')
    code = fields.Char(string='Doctor Code', required=True, copy=False)
    sip_no = fields.Char(string='SIP Number', help='Surat Izin Praktik')
    str_no = fields.Char(string='STR Number', help='Surat Tanda Registrasi')
    specialty_id = fields.Many2one('health.specialty', string='Specialty', required=True)
    department_ids = fields.Many2many('health.department', string='Practicing Departments')

    # Financial & Remuneration
    default_fee_percentage = fields.Float(string='Doctor Fee Share (%)', default=70.0,
                                          help='Default revenue split percentage for professional doctor services')

    # National Regulatory Mapping
    ihs_practitioner_id = fields.Char(string='SatuSehat Practitioner ID', index=True,
                                      help='Kemenkes SatuSehat FHIR Practitioner UUID')
    bpjs_doctor_code = fields.Char(string='BPJS Doctor Code', help='Kode dokter bridging BPJS PCare / VClaim')

    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Physician code must be unique!')
    ]
