# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HealthPhysicianSchedule(models.Model):
    _name = 'health.physician.schedule'
    _description = 'Doctor Practice Schedule & Quota'
    _order = 'department_id, day_of_week, start_hour'

    physician_id = fields.Many2one(
        'health.physician',
        string='Dokter / Tenaga Medis',
        required=True,
        ondelete='cascade',
        index=True
    )
    department_id = fields.Many2one(
        'health.department',
        string='Poliklinik / Spesialisasi',
        required=True,
        domain=[('type', '=', 'outpatient')],
        index=True
    )
    day_of_week = fields.Selection([
        ('0', 'Senin'),
        ('1', 'Selasa'),
        ('2', 'Rabu'),
        ('3', 'Kamis'),
        ('4', 'Jumat'),
        ('5', 'Sabtu'),
        ('6', 'Minggu'),
    ], string='Hari Praktik', required=True, default='0')

    start_hour = fields.Float(string='Jam Mulai Praktik', required=True, default=8.0)
    end_hour = fields.Float(string='Jam Selesai Praktik', required=True, default=14.0)
    max_quota = fields.Integer(string='Maksimum Kuota Pasien', default=30, required=True)
    active = fields.Boolean(string='Aktif', default=True)
    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)

    _sql_constraints = [
        ('health_schedule_hour_check', 'CHECK(end_hour > start_hour)', 'Jam selesai praktik harus lebih besar dari jam mulai!')
    ]

    def name_get(self):
        result = []
        days = dict(self._fields['day_of_week'].selection)
        for rec in self:
            day_name = days.get(rec.day_of_week, '')
            start = f"{int(rec.start_hour):02d}:{int((rec.start_hour % 1) * 60):02d}"
            end = f"{int(rec.end_hour):02d}:{int((rec.end_hour % 1) * 60):02d}"
            name = f"{rec.physician_id.name} - {rec.department_id.name} ({day_name} {start}-{end})"
            result.append((rec.id, name))
        return result
