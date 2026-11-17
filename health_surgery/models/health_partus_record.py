# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HealthPartusRecord(models.Model):
    _name = 'health.partus.record'
    _description = 'Catatan Persalinan VK & Partograf (Kala I - IV)'
    _order = 'delivery_time desc, id desc'

    booking_id = fields.Many2one('health.surgical.booking', string='Registrasi Tindakan', ondelete='cascade')
    patient_id = fields.Many2one('health.patient', string='Ibu Bersalin (Pasien)', required=True)
    patient_mrn = fields.Char(related='patient_id.mrn', string='No. Rekam Medis', store=True)
    inpatient_stay_id = fields.Many2one('health.inpatient.stay', string='Admisi Rawat Inap')

    lead_practitioner_id = fields.Many2one('health.physician', string='Dokter Sp.OG / Bidan Utama Penolong', required=True)
    assistant_practitioner_id = fields.Many2one('health.nurse', string='Bidan / Perawat Pendamping')

    delivery_time = fields.Datetime(string='Waktu Bayi Lahir', default=fields.Datetime.now, required=True)
    delivery_type = fields.Selection([
        ('spontaneous', 'Partus Spontan Normal (Belakang Kepala)'),
        ('breech', 'Partus Sungsang (Breech Delivery)'),
        ('vacuum', 'Ekstraksi Vakum'),
        ('forceps', 'Ekstraksi Forceps'),
        ('sc', 'Sectio Caesarea (SC di Kamar Operasi)'),
    ], string='Metode Persalinan', required=True, default='spontaneous')

    # Alur Kala Persalinan
    kala1_duration_hours = fields.Float(string='Lama Kala I (Jam)', default=4.0)
    kala2_duration_minutes = fields.Integer(string='Lama Kala II Mengedan (Menit)', default=30)
    kala3_duration_minutes = fields.Integer(string='Lama Kala III Plasenta Lahir (Menit)', default=15)
    placenta_delivery = fields.Selection([
        ('spontaneous', 'Spontan Lengkap'),
        ('manual', 'Manual Plasenta'),
        ('curettage', 'Kuretase Sisa Plasenta'),
    ], string='Pelepasan Plasenta', default='spontaneous')

    perineal_tear = fields.Selection([
        ('intact', 'Intak (Tanpa Robekan)'),
        ('degree_1', 'Derajat I (Mukosa Vagina)'),
        ('degree_2', 'Derajat II (Otot Perineum)'),
        ('degree_3', 'Derajat III (Sfingter Ani)'),
        ('degree_4', 'Derajat IV (Dinding Mukosa Rektum)'),
    ], string='Derajat Ruptur Perineum', default='degree_1')
    episiotomy = fields.Boolean(string='Dilakukan Tindakan Episiotomi', default=False)

    # Profil Bayi Baru Lahir
    baby_gender = fields.Selection([
        ('male', 'Laki-Laki'),
        ('female', 'Perempuan'),
    ], string='Jenis Kelamin Bayi', required=True, default='male')
    baby_weight_grams = fields.Integer(string='Berat Badan Bayi (Gram)', required=True, default=3100)
    baby_length_cm = fields.Integer(string='Panjang Badan (cm)', default=49)
    head_circumference_cm = fields.Integer(string='Lingkar Kepala (cm)', default=34)

    apgar_minute_1 = fields.Integer(string='APGAR Score Menit Ke-1 (0-10)', default=8)
    apgar_minute_5 = fields.Integer(string='APGAR Score Menit Ke-5 (0-10)', default=10)
    baby_condition = fields.Selection([
        ('vigorous', 'Vigor / Segera Menangis Kuat'),
        ('mild_asphyxia', 'Asfiksia Ringan-Sedang'),
        ('severe_asphyxia', 'Asfiksia Berat'),
        ('stillbirth', 'IUFD / Stillbirth'),
    ], string='Kondisi Klinis Neonatus', default='vigorous')

    imd_performed = fields.Boolean(string='Inisiasi Menyusu Dini (IMD) Dilakukan >= 1 Jam', default=True)
    notes = fields.Text(string='Catatan Observasi Khusus Kala IV')
    company_id = fields.Many2one('res.company', string='Rumah Sakit', default=lambda self: self.env.company)
