# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class HealthInacbgClaim(models.Model):
    _name = 'health.inacbg.claim'
    _description = 'Berkas Klaim INA-CBG & Audit Disparitas Biaya RS'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='No. Berkas Klaim', required=True, copy=False, readonly=True, default=lambda self: _('Draft Klaim'))
    sep_id = fields.Many2one('health.bpjs.sep', string='Nomor SEP BPJS', required=True, tracking=True)
    nomor_sep = fields.Char(related='sep_id.name', string='No. SEP Resmi', store=True)
    patient_id = fields.Many2one(related='sep_id.patient_id', string='Pasien', store=True)
    patient_mrn = fields.Char(related='sep_id.patient_mrn', string='No. Rekam Medis')
    patient_gender = fields.Selection(related='sep_id.patient_gender', string='Jenis Kelamin')
    patient_age = fields.Integer(related='sep_id.patient_age', string='Usia (Tahun)')

    jenis_pelayanan = fields.Selection(related='sep_id.jenis_pelayanan', string='Jenis Pelayanan', store=True)
    inpatient_stay_id = fields.Many2one('health.inpatient.stay', string='Admisi Rawat Inap Asal')
    surgery_booking_id = fields.Many2one('health.surgical.booking', string='Tindakan Bedah Asal')
    billing_id = fields.Many2one('health.billing.ledger', string='Faktur Billing Riil RS')

    los_days = fields.Integer(string='Lama Rawat (Hari / LOS)', default=3)
    discharge_status = fields.Selection([
        ('1', '1 - Sembuh / Atas Persetujuan DPJP'),
        ('2', '2 - Dirujuk ke Fasilitas Lebih Tinggi'),
        ('3', '3 - Meninggal Dunia'),
        ('4', '4 - Pulang Paksa (Atas Permintaan Sendiri)'),
    ], string='Status Pulang Pasien', default='1', required=True)

    # Diagnosa & Tindakan Koding
    primary_diagnosis_id = fields.Many2one('health.icd10', string='Diagnosa Utama (ICD-10)', required=True)
    secondary_diagnosis_ids = fields.Many2many('health.icd10', 'health_inacbg_claim_icd10_rel', 'claim_id', 'icd10_id', string='Diagnosa Sekunder / Komorbiditas')
    procedure_ids = fields.Many2many('health.surgical.procedure', 'health_inacbg_claim_proc_rel', 'claim_id', 'proc_id', string='Prosedur Tindakan (ICD-9 CM)')

    # Hasil Grouping INA-CBG
    cbg_code = fields.Char(string='Kode INA-CBG', readonly=True, tracking=True)
    cbg_description = fields.Char(string='Deskripsi Kelompok Case-Mix', readonly=True)
    severity_level = fields.Selection([
        ('1', 'Tingkat I (Ringan - Minor)'),
        ('2', 'Tingkat II (Sedang - Moderate)'),
        ('3', 'Tingkat III (Berat - Major)'),
    ], string='Tingkat Keparahan Severity', default='1')

    currency_id = fields.Many2one('res.currency', string='Mata Uang', default=lambda self: self.env.company.currency_id)
    base_tariff = fields.Monetary(string='Tarif Dasar INA-CBG (Plafon Klaim)', currency_field='currency_id', default=0.0, readonly=True)
    special_cmg_code = fields.Char(string='Kode Top-Up Special CMG')
    special_cmg_tariff = fields.Monetary(string='Tarif Tambahan Special CMG', currency_field='currency_id', default=0.0)
    total_inacbg_tariff = fields.Monetary(string='Total Plafon Klaim INA-CBG', currency_field='currency_id', compute='_compute_total_inacbg_tariff', store=True)

    # Analisis Disparitas Biaya (Audit Mutu & Biaya)
    hospital_real_bill = fields.Monetary(string='Biaya Riil Rumah Sakit', currency_field='currency_id', default=0.0, help='Total akumulasi tagihan obat, prosedur, kamar, dan tindakan riil pasien di RS')
    tariff_disparity = fields.Monetary(string='Disparitas Biaya (Margin Klaim)', currency_field='currency_id', compute='_compute_disparity', store=True)
    margin_status = fields.Selection([
        ('surplus', 'Surplus Klaim (Plafon > Biaya Riil)'),
        ('deficit', 'Defisit Biaya (Biaya Riil Melebihi Plafon)'),
        ('balanced', 'Sesuai Plafon (Impas)'),
    ], string='Status Margin Kendali Biaya', compute='_compute_disparity', store=True)

    state = fields.Selection([
        ('draft', 'Pengumpulan Berkas'),
        ('grouped', 'Grouping Stage 1 Selesai'),
        ('finalized', 'Klaim Final (Terkunci)'),
        ('sent_dc', 'Terkirim ke DC Kemenkes'),
    ], string='Status Klaim', default='draft', tracking=True)

    company_id = fields.Many2one('res.company', string='Rumah Sakit', default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Draft Klaim')) == _('Draft Klaim'):
                vals['name'] = self.env['ir.sequence'].next_by_code('health.inacbg.claim') or _('CLM/%s') % fields.Date.today().strftime('%Y%m%d')
        return super().create(vals_list)

    @api.depends('base_tariff', 'special_cmg_tariff')
    def _compute_total_inacbg_tariff(self):
        for rec in self:
            rec.total_inacbg_tariff = rec.base_tariff + rec.special_cmg_tariff

    @api.depends('total_inacbg_tariff', 'hospital_real_bill')
    def _compute_disparity(self):
        for rec in self:
            margin = rec.total_inacbg_tariff - rec.hospital_real_bill
            rec.tariff_disparity = margin
            if margin > 0:
                rec.margin_status = 'surplus'
            elif margin < 0:
                rec.margin_status = 'deficit'
            else:
                rec.margin_status = 'balanced'

    def action_run_grouping(self):
        """Simulates or executes INA-CBG Case-Based Grouping."""
        for rec in self:
            # Deterministic simulation based on primary diagnosis and procedures
            diag_code = rec.primary_diagnosis_id.code or 'A00'
            has_surgery = bool(rec.procedure_ids)
            
            if has_surgery:
                # Surgical CBG e.g. O-6-10 (Sectio) or I-4-10
                if any('SC' in (p.code or '') for p in rec.procedure_ids):
                    rec.cbg_code = 'O-6-10-I' if rec.severity_level == '1' else 'O-6-10-II'
                    rec.cbg_description = 'PERSALINAN DENGAN SECTIO CAESAREA'
                    rec.base_tariff = 5850000.0 if rec.severity_level == '1' else 7420000.0
                else:
                    rec.cbg_code = 'I-4-10-I'
                    rec.cbg_description = 'PROSEDUR BEDAH INTRA-ABDOMEN LAIN'
                    rec.base_tariff = 4920000.0
            else:
                # Medical CBG
                rec.cbg_code = 'A-4-14-I' if rec.severity_level == '1' else 'A-4-14-II'
                rec.cbg_description = f"INFEKSI SALURAN CERNA / GASTROENTERITIS ({diag_code})"
                rec.base_tariff = 2650000.0 if rec.severity_level == '1' else 3850000.0

            # Pull hospital real bill if linked to billing ledger
            if rec.billing_id and hasattr(rec.billing_id, 'total_amount'):
                rec.hospital_real_bill = rec.billing_id.total_amount
            elif not rec.hospital_real_bill:
                # Default baseline real cost for audit comparison
                rec.hospital_real_bill = rec.base_tariff * 0.75

            rec.state = 'grouped'

    def action_finalize_claim(self):
        for rec in self:
            rec.state = 'finalized'

    def action_send_to_dc(self):
        for rec in self:
            rec.state = 'sent_dc'
