# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HealthInpatientTransfer(models.Model):
    _name = 'health.inpatient.transfer'
    _description = 'Inpatient Bed Mutation / Transfer Record'
    _order = 'transfer_date desc, id desc'

    stay_id = fields.Many2one('health.inpatient.stay', string='Pasien Rawat Inap', required=True, ondelete='cascade', index=True)
    patient_id = fields.Many2one('health.patient', related='stay_id.patient_id', string='Pasien', store=True)
    from_bed_id = fields.Many2one('health.bed', string='Tempat Tidur Asal', required=True)
    from_ward_id = fields.Many2one('health.ward', related='from_bed_id.ward_id', string='Bangsal Asal', store=True)
    from_bed_rate = fields.Float(string='Tarif Kamar Asal (Rp)')

    to_bed_id = fields.Many2one('health.bed', string='Tempat Tidur Baru', required=True)
    to_ward_id = fields.Many2one('health.ward', related='to_bed_id.ward_id', string='Bangsal Baru', store=True)
    to_bed_rate = fields.Float(string='Tarif Kamar Baru (Rp)')

    transfer_date = fields.Datetime(string='Waktu Mutasi / Pindah', default=fields.Datetime.now, required=True)
    reason = fields.Char(string='Alasan Pindah Kamar', required=True, default='Peningkatan / Penyesuaian Kelas Perawatan')
    user_id = fields.Many2one('res.users', string='Petugas Mutasi', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)
