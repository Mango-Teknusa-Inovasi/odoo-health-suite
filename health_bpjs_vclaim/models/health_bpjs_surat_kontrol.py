# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HealthBpjsSuratKontrol(models.Model):
    _name = 'health.bpjs.surat.kontrol'
    _description = 'Surat Rencana Kontrol Poliklinik BPJS VClaim 2.0'
    _order = 'tgl_rencana_kontrol desc, id desc'

    name = fields.Char(string='No. Surat Kontrol', required=True, copy=False, readonly=True, default=lambda self: _('Draft Kontrol'))
    no_sep_asal = fields.Char(string='Nomor SEP Rujukan Asal', required=True)
    patient_id = fields.Many2one('health.patient', string='Pasien', required=True)
    patient_mrn = fields.Char(related='patient_id.mrn', string='No. Rekam Medis')
    no_kartu = fields.Char(related='patient_id.bpjs_number', string='Nomor Kartu BPJS')

    tgl_rencana_kontrol = fields.Date(string='Tanggal Rencana Kontrol', required=True, default=fields.Date.today)
    dpjp_id = fields.Many2one('health.physician', string='Dokter DPJP Penerima Kontrol', required=True)
    poli_tujuan_id = fields.Many2one('health.department', string='Poliklinik Tujuan Kontrol', required=True)

    alasan_kontrol = fields.Selection([
        ('followup', 'Pemeriksaan Lanjutan Pasca Rawat Inap (KRS)'),
        ('chronic', 'Pemberian Terapi / Obat Kronis (PRB)'),
        ('eval', 'Evaluasi Hasil Laboratorium / Radiologi'),
    ], string='Indikasi Kontrol', default='followup')

    state = fields.Selection([
        ('draft', 'Draft Pengajuan'),
        ('approved', 'Surat Kontrol Terbit'),
        ('cancelled', 'Dibatalkan'),
    ], string='Status', default='draft')

    company_id = fields.Many2one('res.company', string='Rumah Sakit', default=lambda self: self.env.company)

    def action_approve(self):
        for rec in self:
            seq_val = self.env['ir.sequence'].next_by_code('health.bpjs.surat.kontrol') or fields.Date.today().strftime('%Y%m%d01')
            rec.name = f"SK-{seq_val}"
            rec.state = 'approved'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'
