# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class HealthBpjsSep(models.Model):
    _name = 'health.bpjs.sep'
    _description = 'Surat Eligibilitas Peserta (SEP) BPJS Kesehatan VClaim 2.0'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'tgl_sep desc, id desc'

    name = fields.Char(string='Nomor SEP', required=True, copy=False, readonly=True, default=lambda self: _('Draft SEP'))
    patient_id = fields.Many2one('health.patient', string='Pasien BPJS', required=True, tracking=True)
    patient_mrn = fields.Char(related='patient_id.mrn', string='No. Rekam Medis', store=True)
    no_kartu = fields.Char(related='patient_id.bpjs_number', string='Nomor Kartu BPJS', store=True)
    nik = fields.Char(related='patient_id.nik', string='NIK Pasien', store=True)
    patient_gender = fields.Selection(related='patient_id.gender', string='Jenis Kelamin')
    patient_age = fields.Integer(related='patient_id.age', string='Usia (Tahun)')

    jenis_pelayanan = fields.Selection([
        ('1', 'Rawat Inap'),
        ('2', 'Rawat Jalan (Poliklinik / IGD)'),
    ], string='Jenis Pelayanan', required=True, default='2', tracking=True)

    kelas_rawat = fields.Selection([
        ('1', 'Kelas 1'),
        ('2', 'Kelas 2'),
        ('3', 'Kelas 3'),
    ], string='Hak Kelas Rawat BPJS', default='3')

    tgl_sep = fields.Date(string='Tanggal Terbit SEP', required=True, default=fields.Date.today, tracking=True)
    no_rujukan = fields.Char(string='Nomor Surat Rujukan', default='0195B0010126P000001')
    asal_rujukan = fields.Selection([
        ('1', 'Faskes Tingkat 1 (Puskesmas / Klinik Pratama)'),
        ('2', 'Faskes Tingkat 2 (Rumah Sakit Lain)'),
    ], string='Asal Fasilitas Rujukan', default='1')
    ppk_rujukan = fields.Char(string='Nama / Kode Faskes Perujuk', default='Puskesmas Kedungmungal')

    poli_tujuan_id = fields.Many2one('health.department', string='Poliklinik Tujuan', help='Wajib untuk Rawat Jalan')
    poli_eksekutif = fields.Boolean(string='Poli Eksekutif', default=False)
    dpjp_id = fields.Many2one('health.physician', string='Dokter Penanggung Jawab (DPJP)', required=True)
    diagnosa_awal_id = fields.Many2one('health.icd10', string='Diagnosa Awal ICD-10', required=True)

    no_surat_kontrol = fields.Char(string='No. Surat Kontrol / SPRI')
    spri_id = fields.Many2one('health.bpjs.spri', string='Dokumen SPRI Terkait')
    surat_kontrol_id = fields.Many2one('health.bpjs.surat.kontrol', string='Dokumen Surat Kontrol Terkait')
    inpatient_stay_id = fields.Many2one('health.inpatient.stay', string='Admisi Rawat Inap Terkait')

    catatan = fields.Char(string='Catatan Peserta / Keterangan', default='Peserta JKN Aktif')
    peserta_nama = fields.Char(related='patient_id.name', string='Nama Peserta')
    peserta_jenis = fields.Char(string='Jenis Kepesertaan JKN', default='PBI APBN / Mandiri Kelas 3')

    state = fields.Selection([
        ('draft', 'Pengajuan Draft SEP'),
        ('published', 'SEP Terbit (Aktif)'),
        ('cancelled', 'SEP Dibatalkan'),
    ], string='Status SEP', default='draft', tracking=True)

    company_id = fields.Many2one('res.company', string='Rumah Sakit', default=lambda self: self.env.company)

    def action_generate_sep(self):
        for rec in self:
            config = self.env['health.bpjs.vclaim.config'].search([('company_id', '=', rec.company_id.id)], limit=1)
            ppk = config.ppk_code if config and config.ppk_code else '0195R014'
            now_str = fields.Date.today().strftime('%m%y')
            # Generate official 19-char SEP number: 8-char PPK + 4-char MMyy + 'V' + 6-char sequence
            seq_val = self.env['ir.sequence'].next_by_code('health.bpjs.sep.code') or '000001'
            rec.name = f"{ppk}{now_str}V{seq_val.zfill(6)}"
            rec.state = 'published'

    def action_cancel_sep(self):
        for rec in self:
            rec.state = 'cancelled'

    def action_print_sep(self):
        self.ensure_one()
        return self.env.ref('health_bpjs_vclaim.action_report_health_sep').report_action(self)
