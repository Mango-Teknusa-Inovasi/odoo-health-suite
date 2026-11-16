# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HealthEmrSoap(models.Model):
    _name = 'health.emr.soap'
    _description = 'Clinical Consultation SOAP Notes'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'examination_date desc, name desc'

    name = fields.Char(string='Consultation Reference', required=True, copy=False, readonly=True, default='/')
    patient_id = fields.Many2one('health.patient', string='Patient', required=True, index=True, tracking=True)
    physician_id = fields.Many2one('health.physician', string='Attending Doctor', required=True, index=True, tracking=True)
    department_id = fields.Many2one('health.department', string='Polyclinic / Department', required=True, index=True)
    examination_date = fields.Datetime(string='Examination Date & Time', required=True, default=fields.Datetime.now, tracking=True)

    # Link to Vitals
    vital_sign_id = fields.Many2one('health.vital.sign', string='Vital Signs Record')

    # Subjective (Keluhan & Riwayat)
    chief_complaint = fields.Char(string='Keluhan Utama', required=True, tracking=True)
    subjective = fields.Text(string='S - Subjective (Anamnesis)', required=True)

    # Objective (Pemeriksaan Fisik)
    objective = fields.Text(string='O - Objective (Pemeriksaan Fisik)', required=True)

    # Assessment (Analisis Klinis & Diagnosa)
    assessment = fields.Text(string='A - Assessment (Analisis Medis)')
    diagnosis_line_ids = fields.One2many('health.emr.diagnosis.line', 'soap_id', string='Diagnosis ICD-10 List')

    # Plan (Terapi, Edukasi, Rencana)
    plan = fields.Text(string='P - Plan (Instruksi & Edukasi Medis)', required=True)

    state = fields.Selection([
        ('draft', 'Dalam Pemeriksaan'),
        ('done', 'Selesai / Terverifikasi'),
        ('cancelled', 'Dibatalkan'),
    ], string='Status Konsultasi', default='draft', tracking=True)

    # Medical Certificates & Documents
    sick_leave_days = fields.Integer(string='Hari Istirahat Sakit', default=0)
    sick_leave_start_date = fields.Date(string='Mulai Istirahat')
    sick_leave_end_date = fields.Date(string='Sampai Tanggal')

    company_id = fields.Many2one('res.company', string='Facility', default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('health.emr.soap') or '/'
        return super(HealthEmrSoap, self).create(vals_list)

    def action_validate(self):
        for rec in self:
            if not rec.diagnosis_line_ids:
                raise ValidationError(_('Minimal satu diagnosa ICD-10 harus diisi sebelum menyelesaikan pemeriksaan!'))
            primary_diag = rec.diagnosis_line_ids.filtered(lambda d: d.diagnosis_type == 'primary')
            if not primary_diag:
                raise ValidationError(_('Harus ditentukan satu Diagnosa Utama (Primary Diagnosis)!'))
            rec.state = 'done'

    def action_set_draft(self):
        for rec in self:
            rec.state = 'draft'


class HealthEmrDiagnosisLine(models.Model):
    _name = 'health.emr.diagnosis.line'
    _description = 'SOAP Diagnosis Detail Line'
    _order = 'diagnosis_type, id'

    soap_id = fields.Many2one('health.emr.soap', string='SOAP Consultation', required=True, ondelete='cascade')
    diagnosis_id = fields.Many2one('health.diagnosis', string='Diagnosis (ICD-10)', required=True)
    diagnosis_type = fields.Selection([
        ('primary', 'Diagnosa Utama (Primary)'),
        ('secondary', 'Diagnosa Sekunder (Komplikasi/Penyerta)'),
    ], string='Tipe Diagnosa', required=True, default='secondary')
    clinical_notes = fields.Char(string='Keterangan Tambahan')
