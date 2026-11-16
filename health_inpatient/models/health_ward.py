# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HealthWard(models.Model):
    _name = 'health.ward'
    _description = 'Hospital Ward / Pavilion / Building Unit'
    _order = 'building, floor, name'

    name = fields.Char(string='Nama Bangsal / Paviliun', required=True, index=True)
    code = fields.Char(string='Kode Bangsal', required=True, index=True)
    department_id = fields.Many2one(
        'health.department',
        string='Departemen Rawat Inap',
        domain=[('type', '=', 'inpatient')],
        index=True
    )
    building = fields.Char(string='Gedung', default='Gedung Utama')
    floor = fields.Char(string='Lantai', default='Lantai 1')
    nurse_station = fields.Char(string='Nurse Station / Pos Perawat')

    active = fields.Boolean(string='Aktif', default=True)
    bed_ids = fields.One2many('health.bed', 'ward_id', string='Daftar Tempat Tidur')
    bed_count = fields.Integer(string='Kapasitas Ranjang', compute='_compute_bed_metrics', store=True)
    occupied_bed_count = fields.Integer(string='Ranjang Terisi', compute='_compute_bed_metrics', store=True)
    available_bed_count = fields.Integer(string='Ranjang Tersedia', compute='_compute_bed_metrics', store=True)
    bor_rate = fields.Float(string='Bed Occupancy Rate (BOR %)', compute='_compute_bed_metrics', store=True)

    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)

    _sql_constraints = [
        ('health_ward_code_unique', 'unique(code, company_id)', 'Kode bangsal/paviliun harus unik per faskes!')
    ]

    @api.depends('bed_ids.state')
    def _compute_bed_metrics(self):
        for rec in self:
            total = len(rec.bed_ids)
            occupied = len(rec.bed_ids.filtered(lambda b: b.state == 'occupied'))
            available = len(rec.bed_ids.filtered(lambda b: b.state == 'available'))
            rec.bed_count = total
            rec.occupied_bed_count = occupied
            rec.available_bed_count = available
            rec.bor_rate = (occupied / total * 100.0) if total > 0 else 0.0
