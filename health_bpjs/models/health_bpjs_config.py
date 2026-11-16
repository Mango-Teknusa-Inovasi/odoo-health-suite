# -*- coding: utf-8 -*-
import requests
import json
import time
import hmac
import hashlib
import base64
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class HealthBpjsConfig(models.Model):
    _name = 'health.bpjs.config'
    _description = 'BPJS Kesehatan PCare FKTP Gateway Configuration'
    _order = 'id desc'

    name = fields.Char(string='Nama Konfigurasi', required=True, default='BPJS PCare Sandbox / Production')
    environment = fields.Selection([
        ('sandbox', 'Development / Sandbox PCare'),
        ('production', 'BPJS Kesehatan Production'),
    ], string='Lingkungan Server', required=True, default='sandbox')

    cons_id = fields.Char(string='Consumer ID (Cons ID)', required=True, help='BPJS Consumer ID resmi')
    secret_key = fields.Char(string='Secret Key', required=True, help='BPJS Consumer Secret')
    user_key = fields.Char(string='User Key PCare', required=True, help='BPJS PCare Web Service User Key')
    pcare_username = fields.Char(string='Username Petugas PCare', required=True)
    pcare_password = fields.Char(string='Password Petugas PCare', required=True)
    kd_aplikasi = fields.Char(string='Kode Aplikasi', default='095', required=True)

    base_url = fields.Char(string='Base URL Gateway', compute='_compute_base_url', store=True, readonly=False)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)

    @api.depends('environment')
    def _compute_base_url(self):
        for rec in self:
            if rec.environment == 'production':
                rec.base_url = 'https://apijkn.bpjs-kesehatan.go.id/pcare-rest-v3.0'
            else:
                rec.base_url = 'https://apijkn-dev.bpjs-kesehatan.go.id/pcare-rest-dev'

    def get_auth_headers(self):
        """Generates BPJS timestamp, HMAC-SHA256 signature, and authorization headers."""
        self.ensure_one()
        timestamp = str(int(time.time()))
        data = f"{self.cons_id}&{timestamp}"
        signature = base64.b64encode(
            hmac.new(self.secret_key.encode('utf-8'), data.encode('utf-8'), hashlib.sha256).digest()
        ).decode('utf-8')

        auth_string = f"{self.pcare_username}:{self.pcare_password}:{self.kd_aplikasi}"
        encoded_auth = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

        return {
            'X-cons-id': self.cons_id,
            'X-Timestamp': timestamp,
            'X-Signature': signature,
            'X-Authorization': f"Basic {encoded_auth}",
            'user_key': self.user_key,
            'Content-Type': 'application/json; charset=utf-8',
        }

    def action_test_connection(self):
        self.ensure_one()
        try:
            headers = self.get_auth_headers()
            url = f"{self.base_url}/diagnosa/0/1"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Koneksi Berhasil!'),
                        'message': _('Terhubung dengan gateway BPJS PCare (%s). Response Code: %d') % (self.environment, response.status_code),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(_("Koneksi ditolak oleh gateway BPJS (%d): %s") % (response.status_code, response.text[:200]))
        except Exception as e:
            raise UserError(_("Gagal menghubungi server BPJS PCare: %s") % str(e))
