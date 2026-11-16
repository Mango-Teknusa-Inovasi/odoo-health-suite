# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HealthLabCategory(models.Model):
    _name = 'health.lab.category'
    _description = 'Laboratory Section / Discipline'
    _order = 'sequence, name'

    name = fields.Char(string='Nama Bagian Lab', required=True, index=True)
    code = fields.Char(string='Kode Bagian', required=True, index=True)
    sequence = fields.Integer(string='Urutan', default=10)
    active = fields.Boolean(string='Aktif', default=True)
    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)

    _sql_constraints = [
        ('health_lab_category_code_unique', 'unique(code, company_id)', 'Kode kategori lab harus unik per faskes!')
    ]


class HealthLabTest(models.Model):
    _name = 'health.lab.test'
    _description = 'Laboratory Examination Panel'
    _order = 'category_id, sequence, name'

    name = fields.Char(string='Nama Pemeriksaan Lab', required=True, index=True)
    code = fields.Char(string='Kode Pemeriksaan', required=True, index=True)
    category_id = fields.Many2one('health.lab.category', string='Bidang / Bagian Lab', required=True, index=True)
    sequence = fields.Integer(string='Urutan', default=10)

    sample_type = fields.Selection([
        ('edta_blood', 'Darah EDTA (Hematologi)'),
        ('clot_blood', 'Darah Beku / Serum (Kimia)'),
        ('citrate_blood', 'Darah Sitrat (Koagulasi)'),
        ('urine', 'Urin Segar / Sewaktu'),
        ('sputum', 'Sputum / Dahak BTA'),
        ('swab', 'Swab Nasofaring / Tenggorok'),
        ('feces', 'Feses Rutin'),
        ('csf', 'Cairan Serebrospinal (LCS)'),
        ('other', 'Spesimen Lainnya'),
    ], string='Jenis Sampel / Spesimen', default='edta_blood', required=True)

    specimen_container = fields.Selection([
        ('lavender_top', 'Tabung Tutup Ungu (K2/K3 EDTA)'),
        ('red_top', 'Tabung Tutup Merah (Plain Serum)'),
        ('yellow_top', 'Tabung Tutup Kuning (SST Gel Separator)'),
        ('blue_top', 'Tabung Tutup Biru (Natrium Sitrat)'),
        ('sterile_pot', 'Wadah Pot Steril (Urin/Dahak)'),
        ('other', 'Wadah Lainnya'),
    ], string='Wadah Spesimen', default='lavender_top')

    tariff = fields.Float(string='Tarif Pemeriksaan (Rp)', default=75000.0, required=True)
    estimated_duration_minutes = fields.Integer(string='Estimasi Waktu Hasil (Menit)', default=60)
    parameter_ids = fields.One2many('health.lab.parameter', 'test_id', string='Parameter Pemeriksaan')
    parameter_count = fields.Integer(string='Jumlah Parameter', compute='_compute_parameter_count')

    active = fields.Boolean(string='Aktif', default=True)
    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)

    _sql_constraints = [
        ('health_lab_test_code_unique', 'unique(code, company_id)', 'Kode pemeriksaan lab harus unik per faskes!')
    ]

    @api.depends('parameter_ids')
    def _compute_parameter_count(self):
        for rec in self:
            rec.parameter_count = len(rec.parameter_ids)


class HealthLabParameter(models.Model):
    _name = 'health.lab.parameter'
    _description = 'Laboratory Analyte Parameter'
    _order = 'test_id, sequence, name'

    name = fields.Char(string='Nama Parameter / Analit', required=True, index=True)
    code = fields.Char(string='Kode Parameter', required=True, index=True)
    loinc_code = fields.Char(string='Kode LOINC (SatuSehat FHIR)', help='Kode standar LOINC untuk integrasi FHIR Observation')
    test_id = fields.Many2one('health.lab.test', string='Paket Pemeriksaan', required=True, ondelete='cascade', index=True)
    sequence = fields.Integer(string='Urutan', default=10)

    unit = fields.Char(string='Satuan Ukur (Unit)', default='g/dL')
    result_type = fields.Selection([
        ('numeric', 'Kuantitatif (Angka)'),
        ('qualitative', 'Kualitatif (Positif / Negatif)'),
        ('text', 'Teks Naratif / Deskriptif'),
    ], string='Tipe Hasil', default='numeric', required=True)

    methodology = fields.Char(string='Metode Pemeriksaan', default='Automated Analyzer / Spektrofotometri')
    reference_ids = fields.One2many('health.lab.reference.range', 'parameter_id', string='Rentang Nilai Normal')
    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)


class HealthLabReferenceRange(models.Model):
    _name = 'health.lab.reference.range'
    _description = 'Age & Gender Specific Lab Reference Range'
    _order = 'parameter_id, gender, age_min_years'

    parameter_id = fields.Many2one('health.lab.parameter', string='Parameter Lab', required=True, ondelete='cascade', index=True)
    gender = fields.Selection([
        ('both', 'Semua Gender (L/P)'),
        ('male', 'Laki-Laki'),
        ('female', 'Perempuan'),
    ], string='Jenis Kelamin', default='both', required=True)

    age_min_years = fields.Integer(string='Usia Minimal (Tahun)', default=0)
    age_max_years = fields.Integer(string='Usia Maksimal (Tahun)', default=120)
    age_group_label = fields.Char(string='Label Kelompok Usia', default='Dewasa')

    # Normal Boundaries
    min_val = fields.Float(string='Batas Bawah Normal (Min)')
    max_val = fields.Float(string='Batas Atas Normal (Max)')
    normal_text = fields.Char(string='Teks Normal (Kualitatif)', default='Negatif / Non-Reaktif')

    # Panic / Critical Values (KARS / STARKES Emergency)
    critical_low = fields.Float(string='Nilai Kritis Bawah (Panic Low)', help='Jika hasil di bawah batas ini, sistem akan memicu peringatan darurat')
    critical_high = fields.Float(string='Nilai Kritis Atas (Panic High)', help='Jika hasil di atas batas ini, sistem akan memicu peringatan darurat')
