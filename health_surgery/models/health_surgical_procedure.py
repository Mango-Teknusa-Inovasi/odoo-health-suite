# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HealthSurgicalProcedure(models.Model):
    _name = 'health.surgical.procedure'
    _description = 'Katalog Tindakan Operasi & Prosedur Kebidanan'
    _order = 'category desc, name asc'

    name = fields.Char(string='Nama Tindakan Bedah / Prosedur', required=True)
    code = fields.Char(string='Kode Tindakan', required=True)
    icd9_id = fields.Many2one('health.icd9', string='Kategori Kode ICD-9 CM', help='Kode standar prosedur internasional untuk klaim INA-CBG')
    
    category = fields.Selection([
        ('khusus', 'Operasi Khusus (Jantung / Bedah Saraf / Kompleks)'),
        ('besar', 'Operasi Besar (Laparotomi / SC / Craniotomi)'),
        ('sedang', 'Operasi Sedang (Apendektomi / Herniorafi)'),
        ('kecil', 'Operasi Kecil (Eksisi Lipoma / Sirkumsisi)'),
        ('partus', 'Persalinan Spontan / Normal (VK)'),
    ], string='Tingkat Klasifikasi Pembedahan', required=True, default='sedang')

    estimated_duration_minutes = fields.Integer(string='Estimasi Durasi (Menit)', default=90)
    requires_anesthesia = fields.Boolean(string='Wajib Pendampingan Dokter Anestesi', default=True)
    requires_pediatrician = fields.Boolean(string='Wajib Pendampingan Dokter Anak (Sp.A)', default=False, help='Biasanya diaktifkan untuk tindakan Sectio Caesarea')

    currency_id = fields.Many2one('res.currency', string='Mata Uang', default=lambda self: self.env.company.currency_id)
    operator_fee = fields.Monetary(string='Honor Dokter Operator', currency_field='currency_id', default=1500000.0)
    anesthesia_fee = fields.Monetary(string='Honor Dokter Anestesi', currency_field='currency_id', default=750000.0)
    room_rent_fee = fields.Monetary(string='Sewa Ruang Operasi (OK / VK)', currency_field='currency_id', default=1000000.0)
    consumables_fee = fields.Monetary(string='BHP & Kassa Steril Bedah', currency_field='currency_id', default=500000.0)
    total_procedure_tariff = fields.Monetary(string='Total Tarif Paket Tindakan', currency_field='currency_id', compute='_compute_total_tariff', store=True)

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Rumah Sakit', default=lambda self: self.env.company)

    @api.depends('operator_fee', 'anesthesia_fee', 'room_rent_fee', 'consumables_fee')
    def _compute_total_tariff(self):
        for rec in self:
            rec.total_procedure_tariff = (
                rec.operator_fee +
                rec.anesthesia_fee +
                rec.room_rent_fee +
                rec.consumables_fee
            )
