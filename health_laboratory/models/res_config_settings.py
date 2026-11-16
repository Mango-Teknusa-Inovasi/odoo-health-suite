# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    health_lab_tracking_mode = fields.Selection([
        ('two_step', 'Standar Rumah Sakit: 2 Tahap Pelacakan Sampel (Ambil di Ruangan -> Diterima Lab)'),
        ('direct', 'Klinik / TPMD: 1 Tahap Langsung (Input Hasil Langsung Tanpa Kurir)'),
    ], string='Mode Pelacakan Sampel Lab',
       default='two_step',
       config_parameter='health_laboratory.tracking_mode')

    health_lab_default_pathologist_id = fields.Many2one(
        'health.physician',
        string='Dokter Spesialis Patologi Klinik (Sp.PK) Utama',
        config_parameter='health_laboratory.default_pathologist_id'
    )
