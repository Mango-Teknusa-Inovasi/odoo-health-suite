# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    health_inpatient_calculation_mode = fields.Selection([
        ('cutoff_noon', 'Standar RS (Cut-off Jam 12:00 Siang)'),
        ('rolling_24h', 'Rolling 24 Jam sejak Waktu Masuk'),
    ], string='Metode Perhitungan Hari Rawat',
       default='cutoff_noon',
       config_parameter='health_inpatient.calculation_mode')

    health_inpatient_cutoff_hour = fields.Float(
        string='Jam Cut-Off Ganti Hari Rawat',
        default=12.0,
        config_parameter='health_inpatient.cutoff_hour'
    )
