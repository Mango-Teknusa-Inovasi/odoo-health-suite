# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HealthInpatientDischargeSummary(models.Model):
    _name = 'health.inpatient.discharge.summary'
    _description = 'Inpatient Electronic Discharge Summary (Resume Medis KRS)'
    _order = 'discharge_date desc, id desc'

    stay_id = fields.Many2one('health.inpatient.stay', string='Pasien Rawat Inap', required=True, ondelete='cascade', index=True)
    patient_id = fields.Many2one('health.patient', related='stay_id.patient_id', string='Pasien', store=True)
    medical_record_no = fields.Char(related='stay_id.medical_record_no', string='No. Rekam Medis', store=True)
    physician_id = fields.Many2one('health.physician', related='stay_id.physician_id', string='Dokter DPJP', store=True)

    admission_date = fields.Datetime(related='stay_id.admission_date', string='Waktu Masuk', readonly=True)
    discharge_date = fields.Datetime(related='stay_id.discharge_date', string='Waktu Pulang', readonly=True)
    length_of_stay = fields.Float(related='stay_id.length_of_stay', string='Lama Rawat (Hari)', readonly=True)

    primary_diagnosis_id = fields.Many2one('health.diagnosis', string='Diagnosis Utama Akhir (ICD-10)', required=True)
    secondary_diagnosis_ids = fields.Many2many('health.diagnosis', 'rel_discharge_summary_sec_diag', string='Diagnosis Sekunder (Komorbid)')
    procedure_ids = fields.Many2many('health.procedure', 'rel_discharge_summary_procedure', string='Tindakan / Prosedur Operasi (ICD-9 CM)')

    clinical_summary = fields.Text(string='Ringkasan Riwayat Penyakit & Pengobatan Selama Rawat', required=True)
    physical_findings = fields.Text(string='Pemeriksaan Fisik Terakhir Saat Pulang')
    lab_summary = fields.Text(string='Hasil Pemeriksaan Penunjang (Lab / Radiologi) Penting')
    home_medication = fields.Text(string='Terapi Obat Pulang (Aturan Pakai & Dosis)', required=True)

    discharge_condition = fields.Selection([
        ('good', 'Sembuh / Mandiri'),
        ('fair', 'Membaik / Butuh Bantuan Parsial'),
        ('poor', 'Perlu Perawatan Lanjutan Total'),
    ], string='Kondisi Saat Keluar', default='good', required=True)

    follow_up_instructions = fields.Text(string='Instruksi Kontrol Kembali & Diet', default='Kontrol kembali ke Poliklinik sesuai jadwal. Minum obat teratur.')
    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)
