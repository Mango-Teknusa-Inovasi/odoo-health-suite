# -*- coding: utf-8 -*-
import requests
import json
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class HealthBpjsKunjungan(models.Model):
    _name = 'health.bpjs.kunjungan'
    _description = 'BPJS PCare Outpatient Encounter Bridging'
    _order = 'tgl_kunjungan desc, id desc'

    name = fields.Char(string='No. Kunjungan BPJS', readonly=True, copy=False, default='/')
    appointment_id = fields.Many2one('health.appointment', string='Kunjungan Rawat Jalan', required=True, index=True)
    patient_id = fields.Many2one('health.patient', related='appointment_id.patient_id', string='Pasien', store=True)
    no_kartu = fields.Char(string='No. Kartu BPJS (13 Digit)', required=True)
    tgl_kunjungan = fields.Date(string='Tanggal Kunjungan', default=fields.Date.context_today, required=True)

    kd_poli = fields.Char(string='Kode Poli BPJS', default='001', required=True,
                          help='cth. 001 Poli Umum, 002 Poli Gigi, 003 Poli KIA')
    keluhan = fields.Text(string='Keluhan Pasien', required=True)

    kd_kesadaran = fields.Selection([
        ('01', 'Compos Mentis'),
        ('02', 'Somnolence'),
        ('03', 'Sopor'),
        ('04', 'Coma'),
    ], string='Tingkat Kesadaran', default='01', required=True)

    sistole = fields.Integer(string='Sistole (mmHg)', default=120)
    diastole = fields.Integer(string='Diastole (mmHg)', default=80)
    berat_badan = fields.Float(string='Berat Badan (kg)', default=60.0)
    tinggi_badan = fields.Float(string='Tinggi Badan (cm)', default=165.0)
    resp_rate = fields.Integer(string='Respiratory Rate (/menit)', default=20)
    heart_rate = fields.Integer(string='Heart Rate (/menit)', default=80)

    diagnosis_id = fields.Many2one('health.diagnosis', string='Diagnosis Utama (ICD-10)', required=True)
    status_pulang = fields.Selection([
        ('1', 'Berobat Jalan / Selesai'),
        ('2', 'Rujuk Internal (Poli Lain)'),
        ('3', 'Rujuk Lanjut (FKRTL / Rumah Sakit)'),
        ('4', 'Meninggal Dunia'),
    ], string='Status Pulang', default='1', required=True)

    state = fields.Selection([
        ('draft', 'Draft / Belum Terkirim'),
        ('pending', 'Dalam Antrean Outbox'),
        ('sent', 'Terkirim ke BPJS (201)'),
        ('failed', 'Gagal / Perlu Retry'),
    ], string='Status Bridging', default='draft', index=True)

    log_id = fields.Many2one('health.integration.log', string='Log Outbox Bridging', readonly=True)
    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)

    @api.onchange('appointment_id')
    def _onchange_appointment_id(self):
        if self.appointment_id:
            if self.appointment_id.bpjs_card_no:
                self.no_kartu = self.appointment_id.bpjs_card_no
            elif self.appointment_id.patient_id and self.appointment_id.patient_id.bpjs_card_no:
                self.no_kartu = self.appointment_id.patient_id.bpjs_card_no

            if self.appointment_id.chief_complaint:
                self.keluhan = self.appointment_id.chief_complaint

            # Link vital signs from linked SOAP if available
            if self.appointment_id.soap_id and self.appointment_id.soap_id.vital_sign_id:
                vs = self.appointment_id.soap_id.vital_sign_id
                self.sistole = vs.systolic
                self.diastole = vs.diastolic
                self.berat_badan = vs.weight
                self.tinggi_badan = vs.height
                self.resp_rate = vs.respiratory_rate
                self.heart_rate = vs.heart_rate

            # Link diagnosis from SOAP
            if self.appointment_id.soap_id and self.appointment_id.soap_id.diagnosis_line_ids:
                prim = self.appointment_id.soap_id.diagnosis_line_ids.filtered(lambda d: d.diagnosis_type == 'primary')
                if prim:
                    self.diagnosis_id = prim[0].diagnosis_id.id

    def _build_pcare_payload(self):
        self.ensure_one()
        return {
            'noKartu': self.no_kartu or '',
            'tglDaftar': self.tgl_kunjungan.strftime('%d-%m-%Y') if self.tgl_kunjungan else '',
            'kdPoli': self.kd_poli or '001',
            'keluhan': self.keluhan or '-',
            'kdSadar': self.kd_kesadaran or '01',
            'sistole': int(self.sistole or 120),
            'diastole': int(self.diastole or 80),
            'beratBadan': float(self.berat_badan or 60.0),
            'tinggiBadan': float(self.tinggi_badan or 165.0),
            'respRate': int(self.resp_rate or 20),
            'heartRate': int(self.heart_rate or 80),
            'kdStatusPulang': self.status_pulang or '1',
            'kdDiag1': self.diagnosis_id.code if self.diagnosis_id else 'Z00.0',
        }

    def action_send_to_pcare(self):
        """Dual-Mode: Dispatches immediately to BPJS PCare; on failure or timeout, buffers in health.integration.log for auto-retry."""
        config = self.env['health.bpjs.config'].search([
            ('active', '=', True),
            ('company_id', '=', self.company_id.id)
        ], limit=1)

        for rec in self:
            payload = rec._build_pcare_payload()
            json_str = json.dumps(payload, ensure_ascii=False)
            url = f"{config.base_url}/kunjungan" if config else 'https://apijkn-dev.bpjs-kesehatan.go.id/pcare-rest-dev/kunjungan'

            # Create Outbox Log record
            log = self.env['health.integration.log'].create({
                'service': 'bpjs_pcare',
                'resource_type': 'Kunjungan',
                'endpoint_url': url,
                'http_method': 'POST',
                'request_payload': json_str,
                'state': 'pending',
                'company_id': rec.company_id.id,
            })
            rec.log_id = log.id

            if not config:
                rec.state = 'pending'
                continue

            try:
                headers = config.get_auth_headers()
                response = requests.post(url, headers=headers, json=payload, timeout=8)
                log.response_code = response.status_code
                log.response_body = response.text[:1000]

                if response.status_code in [200, 201]:
                    res_json = response.json()
                    res_data = res_json.get('response', {})
                    if isinstance(res_data, dict) and res_data.get('noKunjungan'):
                        rec.name = res_data.get('noKunjungan')
                    else:
                        rec.name = f"PC/{rec.appointment_id.name}"
                    rec.state = 'sent'
                    log.state = 'success'
                else:
                    rec.state = 'failed'
                    log.state = 'failed'
                    log.error_message = f"BPJS Error ({response.status_code}): {response.text[:200]}"
            except Exception as e:
                # Gateway lag / timeout / unreachable: Buffer into outbox queue
                _logger.warning("BPJS Gateway unreachable or timeout: %s. Queued into Outbox.", str(e))
                rec.state = 'pending'
                log.state = 'pending'
                log.error_message = f"Network Timeout / Offline: {str(e)}"
