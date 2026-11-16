# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    health_pharmacy_fast_track_review = fields.Boolean(
        string='Fast-Track Solo Practice Mode (Bypass Telaah Farmasi)',
        default=False,
        help='Aktifkan mode ini jika dokter merangkap penyerahan obat (cth. Tempat Praktik Mandiri Dokter / TPMD) tanpa apoteker terpisah.',
        config_parameter='health_pharmacy.fast_track_review'
    )
    health_pharmacy_default_tuslah = fields.Float(
        string='Default Tarif Jasa Tuslah Racik (Rp)',
        default=5000.0,
        config_parameter='health_pharmacy.default_tuslah'
    )
    health_pharmacy_default_embalage = fields.Float(
        string='Default Biaya Embalase Wadah/Kertas (Rp)',
        default=500.0,
        config_parameter='health_pharmacy.default_embalage'
    )
