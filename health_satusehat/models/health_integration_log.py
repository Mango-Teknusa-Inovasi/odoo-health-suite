# -*- coding: utf-8 -*-
import requests
import json
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class HealthIntegrationLog(models.Model):
    _name = 'health.integration.log'
    _description = 'Healthcare Regulatory Integration Outbox Queue'
    _order = 'create_date desc, id desc'

    name = fields.Char(string='Transaction Reference', required=True, default='/')
    service = fields.Selection([
        ('satusehat', 'Kemenkes SatuSehat'),
        ('bpjs_pcare', 'BPJS PCare (FKTP)'),
        ('bpjs_vclaim', 'BPJS VClaim (FKRTL)'),
    ], string='Target Service', required=True, default='satusehat', index=True)

    resource_type = fields.Char(string='FHIR Resource / Service Type', required=True, index=True,
                                help='cth. Encounter, Condition, Observation, Patient, SEP')
    endpoint_url = fields.Char(string='Endpoint URL', required=True)
    http_method = fields.Selection([
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
    ], string='HTTP Method', default='POST', required=True)

    request_payload = fields.Text(string='Request JSON Payload')
    response_code = fields.Integer(string='HTTP Response Code')
    response_body = fields.Text(string='Response Body')

    state = fields.Selection([
        ('draft', 'Draft / Queued'),
        ('pending', 'Sedang Dikirim'),
        ('success', 'Sukses (200/201)'),
        ('failed', 'Gagal / Perlu Retry'),
        ('cancelled', 'Dibatalkan'),
    ], string='Status Pengiriman', default='draft', index=True)

    retry_count = fields.Integer(string='Jumlah Retry', default=0)
    error_message = fields.Char(string='Pesan Error')
    company_id = fields.Many2one('res.company', string='Facility', default=lambda self: self.env.company)

    def action_dispatch_now(self):
        """Dispatches the outbox record to the target national gateway."""
        for rec in self:
            rec.state = 'pending'
            # Here we execute request or simulation
            config = self.env['health.satusehat.config'].search([('company_id', '=', rec.company_id.id)], limit=1)
            token = config.access_token if config else 'mock_token'

            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            }

            try:
                # Simulated dispatch if mock or live
                if rec.endpoint_url.startswith('http'):
                    res = requests.request(
                        rec.http_method,
                        rec.endpoint_url,
                        data=rec.request_payload,
                        headers=headers,
                        timeout=15
                    )
                    rec.response_code = res.status_code
                    rec.response_body = res.text
                    if res.status_code in (200, 201):
                        rec.state = 'success'
                        rec.error_message = False
                    else:
                        rec.state = 'failed'
                        rec.retry_count += 1
                        rec.error_message = f"HTTP {res.status_code}: {res.text[:120]}"
                else:
                    # Mock sandbox success
                    rec.response_code = 201
                    rec.response_body = json.dumps({"resourceType": rec.resource_type, "id": "mock-fhir-uuid-12345"})
                    rec.state = 'success'
            except Exception as e:
                rec.state = 'failed'
                rec.retry_count += 1
                rec.error_message = str(e)
