# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HealthVitalSign(models.Model):
    _name = 'health.vital.sign'
    _description = 'Patient Vital Signs Record'
    _order = 'record_date desc'
    _rec_name = 'display_name'

    patient_id = fields.Many2one('health.patient', string='Patient', required=True, index=True, ondelete='cascade')
    record_date = fields.Datetime(string='Record Time', required=True, default=fields.Datetime.now)

    # Blood Pressure
    systolic = fields.Integer(string='Systolic (mmHg)', default=120)
    diastolic = fields.Integer(string='Diastolic (mmHg)', default=80)
    blood_pressure = fields.Char(string='Tensi (TD)', compute='_compute_bp_display', store=True)

    # Vitals
    pulse = fields.Integer(string='Heart Rate / Nadi (bpm)', default=80)
    respiratory_rate = fields.Integer(string='Respirasi / RR (x/mnt)', default=20)
    temperature = fields.Float(string='Suhu Tubuh (°C)', digits=(3, 1), default=36.5)
    spo2 = fields.Integer(string='SpO2 (%)', default=98)

    # Anthropometry & BMI
    weight = fields.Float(string='Berat Badan (kg)', digits=(4, 1), default=60.0)
    height = fields.Float(string='Tinggi Badan (cm)', digits=(4, 1), default=165.0)
    bmi = fields.Float(string='BMI (Indeks Massa Tubuh)', compute='_compute_bmi', store=True, digits=(4, 2))
    bmi_classification = fields.Selection([
        ('underweight', 'Kurus / Underweight (< 18.5)'),
        ('normal', 'Normal (18.5 - 24.9)'),
        ('overweight', 'Kelebihan BB / Overweight (25.0 - 29.9)'),
        ('obese', 'Obesitas (>= 30.0)'),
    ], string='Status Gizi (BMI)', compute='_compute_bmi', store=True)

    # Neurological / Consciousness
    gcs_eye = fields.Integer(string='GCS Eye (1-4)', default=4)
    gcs_verbal = fields.Integer(string='GCS Verbal (1-5)', default=5)
    gcs_motor = fields.Integer(string='GCS Motor (1-6)', default=6)
    gcs_total = fields.Integer(string='Total GCS', compute='_compute_gcs_total', store=True)

    consciousness = fields.Selection([
        ('compos_mentis', 'Compos Mentis (Sadar Penuh)'),
        ('somnolence', 'Somnolence (Mengantuk)'),
        ('sopor', 'Sopor (Stupor)'),
        ('coma', 'Koma'),
        ('apatis', 'Apatis'),
        ('delirium', 'Delirium'),
    ], string='Tingkat Kesadaran', default='compos_mentis')

    clinical_notes = fields.Char(string='Catatan Tambahan')
    display_name = fields.Char(string='Display', compute='_compute_display_name', store=True)

    @api.depends('systolic', 'diastolic')
    def _compute_bp_display(self):
        for rec in self:
            rec.blood_pressure = f"{rec.systolic}/{rec.diastolic} mmHg"

    @api.depends('weight', 'height')
    def _compute_bmi(self):
        for rec in self:
            if rec.height > 0 and rec.weight > 0:
                h_m = rec.height / 100.0
                calc_bmi = round(rec.weight / (h_m * h_m), 2)
                rec.bmi = calc_bmi
                if calc_bmi < 18.5:
                    rec.bmi_classification = 'underweight'
                elif 18.5 <= calc_bmi < 25.0:
                    rec.bmi_classification = 'normal'
                elif 25.0 <= calc_bmi < 30.0:
                    rec.bmi_classification = 'overweight'
                else:
                    rec.bmi_classification = 'obese'
            else:
                rec.bmi = 0.0
                rec.bmi_classification = 'normal'

    @api.depends('gcs_eye', 'gcs_verbal', 'gcs_motor')
    def _compute_gcs_total(self):
        for rec in self:
            rec.gcs_total = (rec.gcs_eye or 4) + (rec.gcs_verbal or 5) + (rec.gcs_motor or 6)

    @api.depends('patient_id.name', 'record_date')
    def _compute_display_name(self):
        for rec in self:
            p_name = rec.patient_id.name or 'Pasien'
            dt = rec.record_date.strftime('%d/%m/%Y %H:%M') if rec.record_date else ''
            rec.display_name = f"TTV - {p_name} ({dt})"
