# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    health_queue_strategy = fields.Selection([
        ('by_department', 'Per Poliklinik (cth. UMUM-001, GIGI-001)'),
        ('by_physician', 'Per Dokter (cth. DOK-01-001)'),
        ('global', 'Satu Antrean Global Terpadu (cth. A-001)'),
        ('custom', 'Custom Prefix Template'),
    ], string='Strategi Penomoran Antrean',
       default='by_department',
       config_parameter='health_appointment.queue_strategy')

    health_queue_custom_prefix = fields.Char(
        string='Custom Prefix Template',
        default='Q-',
        config_parameter='health_appointment.queue_custom_prefix'
    )

    health_queue_auto_call_audio = fields.Boolean(
        string='Aktifkan Audio Synthesizer pada Layar TV',
        default=True,
        config_parameter='health_appointment.queue_auto_call_audio'
    )
