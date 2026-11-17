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

class HealthBpjsVclaimConfig(models.Model):
    _name = 'health.bpjs.vclaim.config'
    _description = 'Konfigurasi BPJS Kesehatan VClaim 2.0 (Rumah Sakit / FKRTL)'
    _order = 'id desc'

    name = fields.Char(string='Nama Konfigurasi', required=True, default='BPJS VClaim 2.0 Gateway')
    environment = fields.Selection([
        ('sandbox', 'Development / Sandbox VClaim'),
        ('production', 'BPJS VClaim Production'),
    ], string='Lingkungan Server', required=True, default='sandbox')

    mode = fields.Selection([
        ('mock', 'Internal Mock Simulator (Offline / Testing)'),
        ('live', 'Live BPJS Gateway (Online Web Service)'),
    ], string='Mode Operasional Bridging', required=True, default='mock', help='Mode mock memungkinkan simulasi penerbitan SEP offline tanpa koneksi VPN BPJS')

    cons_id = fields.Char(string='Consumer ID (Cons ID)', required=True, default='12345')
    secret_key = fields.Char(string='Secret Key', required=True, default='secret123')
    user_key = fields.Char(string='User Key VClaim', required=True, default='userkey_vclaim_999')
    ppk_code = fields.Char(string='Kode PPK Rumah Sakit (BPJS)', required=True, default='0195R014')

    base_url = fields.Char(string='Base URL Gateway', compute='_compute_base_url', store=True, readonly=False)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Rumah Sakit', default=lambda self: self.env.company)

    @api.depends('environment')
    def _compute_base_url(self):
        for rec in self:
            if rec.environment == 'production':
                rec.base_url = 'https://apijkn.bpjs-kesehatan.go.id/vclaim-rest'
            else:
                rec.base_url = 'https://apijkn-dev.bpjs-kesehatan.go.id/vclaim-rest-dev'

    def get_auth_headers(self):
        """Menghasilkan timestamp, HMAC-SHA256 signature, dan header resmi BPJS VClaim."""
        self.ensure_one()
        timestamp = str(int(time.time()))
        data = f"{self.cons_id}&{timestamp}"
        signature = base64.b64encode(
            hmac.new(self.secret_key.encode('utf-8'), data.encode('utf-8'), hashlib.sha256).digest()
        ).decode('utf-8')

        return {
            'X-cons-id': self.cons_id,
            'X-Timestamp': timestamp,
            'X-Signature': signature,
            'user_key': self.user_key,
            'Content-Type': 'application/x-www-form-urlencoded',
        }

    def action_test_connection(self):
        self.ensure_one()
        if self.mode == 'mock':
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Mock Gateway Terhubung!'),
                    'message': _('Mode Mock Simulator VClaim 2.0 aktif dan siap melayani penerbitan SEP.'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        try:
            headers = self.get_auth_headers()
            url = f"{self.base_url}/referensi/diagnosa/A09"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Koneksi VClaim 2.0 Berhasil!'),
                        'message': _('Terhubung dengan gateway BPJS VClaim (%s). Response: %d') % (self.environment, response.status_code),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(_("Gagal terhubung ke BPJS VClaim. HTTP Status: %d\n%s") % (response.status_code, response.text))
        except Exception as e:
            raise UserError(_("Kesalahan koneksi ke BPJS VClaim: %s") % str(e))
