# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HealthBed(models.Model):
    _name = 'health.bed'
    _description = 'Hospital Room & Inpatient Bed'
    _order = 'ward_id, name'

    name = fields.Char(string='Nomor Tempat Tidur / Kamar', required=True, index=True)
    ward_id = fields.Many2one('health.ward', string='Bangsal / Paviliun', required=True, ondelete='cascade', index=True)
    building = fields.Char(related='ward_id.building', string='Gedung', readonly=True)
    floor = fields.Char(related='ward_id.floor', string='Lantai', readonly=True)

    bed_class = fields.Selection([
        ('vvip', 'Kelas VVIP'),
        ('vip', 'Kelas VIP'),
        ('class_1', 'Kelas 1'),
        ('class_2', 'Kelas 2'),
        ('class_3', 'Kelas 3'),
        ('isolation', 'Ruang Isolasi'),
        ('icu', 'ICU / ICCU / PICU / NICU'),
        ('hcu', 'High Care Unit (HCU)'),
    ], string='Kelas Perawatan', default='class_3', required=True)

    state = fields.Selection([
        ('available', 'Tersedia (Kosong)'),
        ('occupied', 'Terisi Pasien'),
        ('cleaning', 'Pembersihan / Sterilisasi'),
        ('reserved', 'Dipesan (Booking)'),
        ('maintenance', 'Perbaikan / Rusak'),
    ], string='Status Ranjang', default='available', index=True)

    daily_rate = fields.Float(string='Tarif Sewa Kamar / Hari (Rp)', default=150000.0, required=True)
    current_stay_id = fields.Many2one('health.inpatient.stay', string='Pasien Rawat Inap Aktif', readonly=True)
    current_patient_id = fields.Many2one('health.patient', related='current_stay_id.patient_id', string='Nama Pasien', readonly=True)

    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)

    _sql_constraints = [
        ('health_bed_name_ward_unique', 'unique(name, ward_id, company_id)', 'Nomor bed harus unik di dalam satu bangsal!')
    ]

    def action_mark_available(self):
        """Sanitation confirmation action: Moves bed from cleaning to available."""
        for rec in self:
            rec.state = 'available'
            rec.current_stay_id = False

    def action_mark_cleaning(self):
        for rec in self:
            rec.state = 'cleaning'
            rec.current_stay_id = False

    def action_mark_maintenance(self):
        for rec in self:
            rec.state = 'maintenance'
