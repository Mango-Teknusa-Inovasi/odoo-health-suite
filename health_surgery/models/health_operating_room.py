# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HealthOperatingRoom(models.Model):
    _name = 'health.operating.room'
    _description = 'Kamar Operasi dan Kamar Bersalin (VK)'
    _order = 'name asc'

    name = fields.Char(string='Nama Ruangan', required=True, tracking=True)
    code = fields.Char(string='Kode Ruang', required=True, copy=False)
    room_type = fields.Selection([
        ('major_or', 'Kamar Operasi Mayor'),
        ('minor_or', 'Kamar Operasi Minor'),
        ('vk_delivery', 'Kamar Bersalin (VK / PONEK)'),
        ('pacu', 'Ruang Pemulihan (PACU / RR)'),
        ('cath_lab', 'Cath Lab (Katerisasi Jantung)'),
    ], string='Jenis Fasilitas Prosedur', required=True, default='major_or')

    building = fields.Char(string='Gedung / Sayap', default='Gedung Bedah Sentral (IBS)')
    floor = fields.Integer(string='Lantai', default=2)
    state = fields.Selection([
        ('available', 'Tersedia / Siap Digunakan'),
        ('in_use', 'Sedang Digunakan Prosedur'),
        ('cleaning', 'Pembersihan & Dekontaminasi'),
        ('maintenance', 'Maintenance / Sterilisasi Udara'),
    ], string='Status Kesiapan', default='available', tracking=True)

    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)
    notes = fields.Text(string='Catatan Fasilitas / Spesifikasi HEPA Filter')
    company_id = fields.Many2one('res.company', string='Rumah Sakit', default=lambda self: self.env.company)

    booking_ids = fields.One2many('health.surgical.booking', 'room_id', string='Daftar Jadwal Operasi')
    current_booking_id = fields.Many2one('health.surgical.booking', string='Operasi Berlangsung Saat Ini', compute='_compute_current_booking')

    def _compute_current_booking(self):
        for rec in self:
            active_booking = self.env['health.surgical.booking'].search([
                ('room_id', '=', rec.id),
                ('state', '=', 'in_progress')
            ], limit=1)
            rec.current_booking_id = active_booking or False

    def action_set_available(self):
        for rec in self:
            rec.state = 'available'

    def action_set_cleaning(self):
        for rec in self:
            rec.state = 'cleaning'
