# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HealthRadiologyTest(models.Model):
    _name = 'health.radiology.test'
    _description = 'Radiology Examination Master'
    _order = 'modality, sequence, name'

    name = fields.Char(string='Nama Tindakan Radiologi', required=True, index=True)
    code = fields.Char(string='Kode Tindakan', required=True, index=True)
    sequence = fields.Integer(string='Urutan', default=10)

    modality = fields.Selection([
        ('xray', 'Rontgen / X-Ray (Konvensional/Digital)'),
        ('usg', 'Ultrasonografi (USG)'),
        ('ct', 'CT-Scan (Computed Tomography)'),
        ('mri', 'Magnetic Resonance Imaging (MRI)'),
        ('mammo', 'Mammografi'),
        ('fluoro', 'Fluoroskopi / C-Arm'),
        ('panoramic', 'Panoramic Gigi &amp; Cephalometri'),
    ], string='Modalitas Radiologi', default='xray', required=True, index=True)

    body_part = fields.Selection([
        ('chest', 'Thorax / Dada'),
        ('abdomen', 'Abdomen / Perut'),
        ('head_neck', 'Kepala, Otak &amp; Leher'),
        ('spine', 'Tulang Belakang / Vertebra'),
        ('extremities', 'Ekstremitas (Tangan / Kaki)'),
        ('pelvis', 'Pelvis &amp; Panggul'),
        ('dental', 'Gigi &amp; Rahang'),
        ('other', 'Bagian Tubuh Lainnya'),
    ], string='Bagian Tubuh', default='chest', required=True)

    tariff = fields.Float(string='Tarif Tindakan (Rp)', default=125000.0, required=True)
    radiation_warning = fields.Boolean(string='Peringatan Radiasi (Kontraindikasi Hamil)', default=True)
    preparation_notes = fields.Text(string='Petunjuk Persiapan Pasien', default='Pakaian khusus radiologi. Lepas seluruh benda dan perhiasan logam.')
    template_findings = fields.Text(string='Template Temuan Standar (Normal)',
                                   default='Cor dan pulmo dalam batas normal. Tidak tampak kardiomegali maupun infiltrat.')

    active = fields.Boolean(string='Aktif', default=True)
    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)

    _sql_constraints = [
        ('health_radiology_test_code_unique', 'unique(code, company_id)', 'Kode tindakan radiologi harus unik per faskes!')
    ]
