# -*- coding: utf-8 -*-
import requests
import json
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class HealthInacbgConfig(models.Model):
    _name = 'health.inacbg.config'
    _description = 'Konfigurasi Server E-Klaim INA-CBG Kemenkes'
    _order = 'id desc'

    name = fields.Char(string='Nama Konfigurasi', required=True, default='Kemenkes E-Klaim Grouper')
    server_url = fields.Char(string='URL Web Service E-Klaim', required=True, default='http://127.0.0.1:80/eklaim/ws.php', help='Alamat IP server lokal aplikasi E-Klaim di intranet RS')
    hospital_code = fields.Char(string='Kode Rumah Sakit (Kemenkes)', required=True, default='3578014')
    coder_nik = fields.Char(string='NIK Petugas Coder Klaim', required=True, default='3578012345670001')
    encryption_key = fields.Char(string='Kunci Enkripsi E-Klaim (Key 64-Hex)', required=True, default='a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90')

    mode = fields.Selection([
        ('mock', 'Internal Mock Simulator (Offline / Testing)'),
        ('live', 'Live E-Klaim Appliance (Intranet RS)'),
    ], string='Mode Operasional Grouper', required=True, default='mock', help='Mode mock memungkinkan simulasi grouping offline dan audit efisiensi tanpa server eklaim fisik')

    tariff_class = fields.Selection([
        ('AP', 'RS Pemerintah Kelas A'),
        ('BP', 'RS Pemerintah Kelas B'),
        ('CP', 'RS Pemerintah Kelas C'),
        ('DP', 'RS Pemerintah Kelas D'),
        ('AS', 'RS Swasta Kelas A'),
        ('BS', 'RS Swasta Kelas B'),
        ('CS', 'RS Swasta Kelas C'),
        ('DS', 'RS Swasta Kelas D'),
    ], string='Kelas Tarif Rumah Sakit INA-CBG', required=True, default='CS')

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Rumah Sakit', default=lambda self: self.env.company)

    def action_test_connection(self):
        self.ensure_one()
        if self.mode == 'mock':
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Mock Grouper Siap!'),
                    'message': _('Simulator Grouper INA-CBG aktif. Mendukung simulasi tarif CBG & audit disparitas.'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        try:
            # Ping E-Klaim WS with metadata check
            payload = {
                "metadata": {
                    "method": "get_claim_data"
                },
                "data": {
                    "nomor_sep": "TEST_PING"
                }
            }
            res = requests.post(self.server_url, json=payload, timeout=5)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Terhubung ke E-Klaim!'),
                    'message': _('Respon server E-Klaim diterima (Status: %d).') % res.status_code,
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            raise UserError(_("Gagal terhubung ke Server E-Klaim: %s") % str(e))
