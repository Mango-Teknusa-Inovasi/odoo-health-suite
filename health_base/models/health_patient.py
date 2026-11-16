# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date

class HealthPatient(models.Model):
    _name = 'health.patient'
    _description = 'Healthcare Patient Master Registry'
    _inherits = {'res.partner': 'partner_id'}
    _order = 'medical_record_no desc, name'

    partner_id = fields.Many2one('res.partner', string='Partner Contact', required=True, ondelete='cascade')
    medical_record_no = fields.Char(string='Medical Record No (No RM)', required=True, copy=False, index=True, default='/')
    nik = fields.Char(string='NIK (National ID)', size=16, index=True, copy=False, help='16-digit Indonesian National ID Number')

    gender = fields.Selection([
        ('male', 'Laki-Laki'),
        ('female', 'Perempuan'),
    ], string='Gender', required=True, default='male')

    birth_date = fields.Date(string='Date of Birth', required=True)
    birth_place = fields.Char(string='Place of Birth')
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    age_display = fields.Char(string='Age Display', compute='_compute_age', store=True)

    mother_name = fields.Char(string='Mother Name (Nama Ibu Kandung)',
                              help='Crucial for resolving duplicate patient records in Indonesian clinics/hospitals')

    blood_type = fields.Selection([
        ('A', 'A'),
        ('B', 'B'),
        ('AB', 'AB'),
        ('O', 'O'),
        ('unknown', 'Tidak Tahu / Belum Cek'),
    ], string='Blood Type', default='unknown')

    rhesus = fields.Selection([
        ('positive', 'Rh (+)'),
        ('negative', 'Rh (-)'),
    ], string='Rhesus', default='positive')

    marital_status = fields.Selection([
        ('single', 'Belum Menikah'),
        ('married', 'Menikah'),
        ('divorced', 'Cerai Hidup'),
        ('widowed', 'Cerai Mati'),
    ], string='Marital Status', default='single')

    religion = fields.Selection([
        ('islam', 'Islam'),
        ('kristen', 'Kristen Protestan'),
        ('katolik', 'Katolik'),
        ('hindu', 'Hindu'),
        ('buddha', 'Buddha'),
        ('khonghucu', 'Khonghucu'),
        ('other', 'Lainnya'),
    ], string='Religion', default='islam')

    occupation = fields.Char(string='Occupation (Pekerjaan)')

    # Emergency Contact
    emergency_contact_name = fields.Char(string='Emergency Contact Name')
    emergency_contact_relation = fields.Char(string='Relation')
    emergency_contact_phone = fields.Char(string='Emergency Contact Phone')

    # Medical History & Clinical Flags
    allergy_notes = fields.Text(string='Allergy Notes (Riwayat Alergi)',
                                help='Catatan alergi obat, makanan, atau zat kimia')
    chronic_disease_notes = fields.Text(string='Chronic Disease Notes (Riwayat Penyakit Kronis)')

    # National Regulatory Mapping
    bpjs_card_no = fields.Char(string='No. Kartu BPJS', size=13, copy=False, index=True)
    ihs_number = fields.Char(string='SatuSehat IHS Patient ID', copy=False, index=True,
                             help='UUID Pasien dari Kemenkes SatuSehat FHIR')

    company_id = fields.Many2one('res.company', string='Facility', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('mrn_unique', 'unique(medical_record_no, company_id)', 'Medical Record Number (No RM) must be unique per facility!'),
    ]

    @api.constrains('nik')
    def _check_nik_format(self):
        for rec in self:
            if rec.nik:
                if len(rec.nik) != 16 or not rec.nik.isdigit():
                    raise ValidationError(_('NIK must be exactly 16 numerical digits!'))

    @api.depends('birth_date')
    def _compute_age(self):
        today = date.today()
        for rec in self:
            if rec.birth_date:
                born = rec.birth_date
                years = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
                # Calculate remaining months
                if today.month >= born.month:
                    months = today.month - born.month
                else:
                    months = 12 + today.month - born.month
                rec.age = years
                rec.age_display = f"{years} Th {months} Bln"
            else:
                rec.age = 0
                rec.age_display = "0 Th"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('medical_record_no') or vals.get('medical_record_no') == '/':
                vals['medical_record_no'] = self.env['ir.sequence'].next_by_code('health.patient.mrn') or '/'
            # Mark partner as is_company = False
            vals['is_company'] = False
        return super(HealthPatient, self).create(vals_list)
