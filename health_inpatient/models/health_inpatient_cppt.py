# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta

class HealthInpatientCppt(models.Model):
    _name = 'health.inpatient.cppt'
    _description = 'Integrated Patient Progress Notes (CPPT) Multi-Profession'
    _order = 'date desc, id desc'

    stay_id = fields.Many2one('health.inpatient.stay', string='Pasien Rawat Inap', required=True, ondelete='cascade', index=True)
    patient_id = fields.Many2one('health.patient', related='stay_id.patient_id', string='Pasien', store=True)
    date = fields.Datetime(string='Waktu Catatan (WITA/WIB/WIT)', default=fields.Datetime.now, required=True, index=True)

    profession = fields.Selection([
        ('dpjp', 'Dokter DPJP Utama'),
        ('physician_consultant', 'Dokter Konsulen'),
        ('nurse', 'Perawat / Bidan'),
        ('pharmacist', 'Apoteker Klinis'),
        ('nutritionist', 'Ahli Gizi / Dietisien'),
        ('physiotherapist', 'Fisioterapis'),
    ], string='Profesi PPA (Pemberi Asuhan)', default='nurse', required=True)

    user_id = fields.Many2one('res.users', string='Petugas / Pencatat', default=lambda self: self.env.user, required=True)

    # Multi-Profession SOAP / SBAR
    subjective = fields.Text(string='S - Subjective (Keluhan & Anamnesis Pasien)', required=True)
    objective = fields.Text(string='O - Objective (Pemeriksaan Fisik, Tanda Vital, Hasil Lab)', required=True)
    assessment = fields.Text(string='A - Assessment (Analisis Klinis / Diagnosa Keperawatan)', required=True)
    plan = fields.Text(string='P - Plan (Instruksi Medis, Terapi, Diet, Intervensi)', required=True)

    # 24-Hour DPJP Verification (KARS / STARKES Compliance)
    dpjp_verified = fields.Boolean(string='Terverifikasi / Paraf DPJP', default=False)
    dpjp_verified_time = fields.Datetime(string='Waktu Paraf DPJP', readonly=True)
    dpjp_id = fields.Many2one('health.physician', string='Dokter DPJP yang Memaraf', readonly=True)
    is_overdue_verification = fields.Boolean(string='Jatuh Tempo Verifikasi (>24 Jam)', compute='_compute_overdue', store=False)

    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)

    @api.depends('date', 'dpjp_verified', 'profession')
    def _compute_overdue(self):
        now = fields.Datetime.now()
        for rec in self:
            if not rec.dpjp_verified and rec.profession != 'dpjp' and rec.date:
                # Flag if older than 24 hours
                rec.is_overdue_verification = (now - rec.date) > timedelta(hours=24)
            else:
                rec.is_overdue_verification = False

    def action_verify_dpjp(self):
        """DPJP marks verification and digital signature for accreditation audit."""
        physician = self.env['health.physician'].search([('user_id', '=', self.env.user.id)], limit=1)
        for rec in self:
            rec.dpjp_verified = True
            rec.dpjp_verified_time = fields.Datetime.now()
            rec.dpjp_id = physician.id if physician else rec.stay_id.physician_id.id
