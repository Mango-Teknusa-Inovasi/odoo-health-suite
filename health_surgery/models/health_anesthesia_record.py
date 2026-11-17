# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HealthAnesthesiaRecord(models.Model):
    _name = 'health.anesthesia.record'
    _description = 'Catatan Anestesi & Pemantauan Sedasi'
    _order = 'id desc'

    booking_id = fields.Many2one('health.surgical.booking', string='Registrasi Operasi', required=True, ondelete='cascade')
    patient_id = fields.Many2one(related='booking_id.patient_id', string='Pasien', store=True)
    anesthesiologist_id = fields.Many2one('health.physician', string='Dokter Anestesi Penanggung Jawab', required=True)

    anesthesia_technique = fields.Selection([
        ('general', 'Anestesi Umum (General Anesthesia - ETT / LMA)'),
        ('spinal', 'Anestesi Regional Spinal (Subarachnoid Block / SAB)'),
        ('epidural', 'Anestesi Regional Epidural'),
        ('nerve_block', 'Blok Saraf Perifer (Plexus Block)'),
        ('local', 'Infiltrasi Lokal / Tumescent'),
        ('sedation', 'Sedasi Sadar / Moderat'),
    ], string='Teknik Anestesi', required=True, default='general')

    asa_score = fields.Selection([
        ('1', 'ASA I — Pasien Sehat Normal'),
        ('2', 'ASA II — Penyakit Sistemik Ringan Terkontrol'),
        ('3', 'ASA III — Penyakit Sistemik Berat Membatasi Aktivitas'),
        ('4', 'ASA IV — Penyakit Berat Mengancam Jiwa Konstan'),
        ('5', 'ASA V — Pasien Kritis Tanpa Operasi Tidak Bertahan 24 Jam'),
        ('e', 'ASA Emergency — Kondisi Cito / Darurat'),
    ], string='Klasifikasi Status Fisik ASA', required=True, default='1')

    airway_type = fields.Selection([
        ('ett', 'Endotracheal Tube (ETT)'),
        ('lma', 'Laryngeal Mask Airway (LMA)'),
        ('mask', 'Face Mask / Kanul Oksigen'),
        ('trachea', 'Trakeostomi / Krikotiroidotomi'),
        ('spontaneous', 'Pernapasan Spontan'),
    ], string='Manajemen Jalan Napas', default='ett')

    ett_size = fields.Float(string='Ukuran ETT / LMA (No.)', default=7.0)
    premedication = fields.Char(string='Obat Pre-Medikasi (e.g. Midazolam, Ondansetron)')
    induction_agents = fields.Char(string='Obat Induksi (e.g. Propofol, Ketamine, Fentanyl)')
    maintenance_agents = fields.Char(string='Inhalasi & Maintenance (e.g. Sevoflurane, Isoflurane, O2)')
    muscle_relaxant = fields.Char(string='Pelumpuh Otot (e.g. Rocuronium, Atracurium)')
    reversal_agents = fields.Char(string='Reversal / Penawar (e.g. Neostigmine + Atropine, Sugammadex)')

    # Fluid & Hemodynamic Balance
    crystalloid_ml = fields.Integer(string='Cairan Kristaloid Masuk (RL / NaCl mL)', default=1000)
    colloid_ml = fields.Integer(string='Cairan Koloid Masuk (mL)', default=0)
    blood_transfusion_ml = fields.Integer(string='Transfusi Darah (PRC / WB mL)', default=0)
    urine_output_ml = fields.Integer(string='Haluaran Urin / Diuresis (mL)', default=200)

    anesthesia_notes = fields.Text(string='Catatan Khusus Selama Anestesi & Pemulihan')
    company_id = fields.Many2one('res.company', string='Rumah Sakit', default=lambda self: self.env.company)
