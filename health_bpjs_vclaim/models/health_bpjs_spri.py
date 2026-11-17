# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HealthBpjsSpri(models.Model):
    _name = 'health.bpjs.spri'
    _description = 'Surat Perintah Rawat Inap (SPRI) BPJS VClaim 2.0'
    _order = 'tgl_rencana_inap desc, id desc'

    name = fields.Char(string='No. SPRI', required=True, copy=False, readonly=True, default=lambda self: _('Draft SPRI'))
    patient_id = fields.Many2one('health.patient', string='Pasien', required=True)
    patient_mrn = fields.Char(related='patient_id.mrn', string='No. Rekam Medis')
    no_kartu = fields.Char(related='patient_id.bpjs_number', string='Nomor Kartu BPJS')

    tgl_rencana_inap = fields.Date(string='Tanggal Rencana Rawat Inap', required=True, default=fields.Date.today)
    dpjp_id = fields.Many2one('health.physician', string='Dokter Penanggung Jawab (DPJP)', required=True)
    department_id = fields.Many2one('health.department', string='Spesialisasi / Poli Pengirim', required=True)
    diagnosa_id = fields.Many2one('health.icd10', string='Indikasi Rawat Inap (Diagnosa ICD-10)', required=True)

    state = fields.Selection([
        ('draft', 'Pengajuan SPRI'),
        ('approved', 'Disetujui DPJP & Terbit'),
        ('cancelled', 'Dibatalkan'),
    ], string='Status SPRI', default='draft')

    company_id = fields.Many2one('res.company', string='Rumah Sakit', default=lambda self: self.env.company)

    def action_approve(self):
        for rec in self:
            seq_val = self.env['ir.sequence'].next_by_code('health.bpjs.spri') or fields.Date.today().strftime('%Y%m%d01')
            rec.name = f"SPRI-{seq_val}"
            rec.state = 'approved'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'
