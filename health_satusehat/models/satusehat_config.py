# -*- coding: utf-8 -*-
import requests
import json
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class SatuSehatConfig(models.Model):
    _name = 'health.satusehat.config'
    _description = 'Kemenkes SatuSehat Gateway Configuration'
    _order = 'id desc'

    name = fields.Char(string='Config Name', required=True, default='SatuSehat Production / Sandbox')
    environment = fields.Selection([
        ('sandbox', 'Development / Sandbox'),
        ('staging', 'Staging Trial'),
        ('production', 'Kemenkes Production'),
    ], string='Environment', required=True, default='sandbox')

    organization_id = fields.Char(string='Organization ID', required=True,
                                  help='Kemenkes SatuSehat Organization ID (cth. 10000004)')
    client_id = fields.Char(string='Client Key (ID)', required=True)
    client_secret = fields.Char(string='Client Secret', required=True)

    auth_url = fields.Char(string='OAuth2 Auth URL', compute='_compute_urls', store=True, readonly=False)
    base_url = fields.Char(string='FHIR Base URL', compute='_compute_urls', store=True, readonly=False)

    access_token = fields.Text(string='Current Access Token', readonly=True)
    token_expiry = fields.Datetime(string='Token Expiry', readonly=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Facility', default=lambda self: self.env.company)

    @api.depends('environment')
    def _compute_urls(self):
        for rec in self:
            if rec.environment == 'production':
                rec.auth_url = 'https://api-satusehat.kemkes.go.id/oauth2/v1'
                rec.base_url = 'https://api-satusehat.kemkes.go.id/fhir-r4/v1'
            elif rec.environment == 'staging':
                rec.auth_url = 'https://api-satusehat-stg.kemkes.go.id/oauth2/v1'
                rec.base_url = 'https://api-satusehat-stg.kemkes.go.id/fhir-r4/v1'
            else:
                rec.auth_url = 'https://api-satusehat-dev.dto.kemkes.go.id/oauth2/v1'
                rec.base_url = 'https://api-satusehat-dev.dto.kemkes.go.id/fhir-r4/v1'

    def action_test_connection(self):
        self.ensure_one()
        token_endpoint = f"{self.auth_url}/accesstoken?grant_type=client_credentials"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        try:
            response = requests.post(token_endpoint, data=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Koneksi SatuSehat Sukses!'),
                        'message': _('Berhasil terhubung ke server Kemenkes SatuSehat OAuth2 dan mendapatkan token.'),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(_('Koneksi gagal (%s): %s') % (response.status_code, response.text))
        except requests.exceptions.RequestException as e:
            raise UserError(_('Gagal terhubung ke host SatuSehat: %s') % str(e))
