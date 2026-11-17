# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HealthSurgicalChecklist(models.Model):
    _name = 'health.surgical.checklist'
    _description = 'WHO Surgical Safety Checklist (KARS / STARKES Compliant)'
    _order = 'id desc'

    booking_id = fields.Many2one('health.surgical.booking', string='Registrasi Operasi', required=True, ondelete='cascade')
    patient_id = fields.Many2one(related='booking_id.patient_id', string='Pasien', store=True)

    # ==========================================================
    # 1. SIGN IN (Sebelum Induksi Anestesi)
    # ==========================================================
    signin_patient_confirmed = fields.Boolean(string='Identitas, Lokasi Operasi, dan Persetujuan Informed Consent Terkonfirmasi', default=False)
    signin_site_marked = fields.Boolean(string='Lokasi Pembedahan Telah Ditandai (Site Marking)', default=False)
    signin_anesthesia_check = fields.Boolean(string='Pemeriksaan Kesiapan Mesin Anestesi & Obat Lengkap', default=False)
    signin_pulse_oximeter = fields.Boolean(string='Pulse Oximeter Terpasang & Berfungsi Baik', default=False)
    signin_known_allergy = fields.Boolean(string='Riwayat Alergi Obat / Makanan Telah Diverifikasi', default=False)
    signin_airway_risk = fields.Boolean(string='Risiko Kesulitan Jalan Napas / Aspirasi Telah Diantisipasi', default=False)
    signin_blood_loss_risk = fields.Boolean(string='Risiko Kehilangan Darah (>500 mL / >7 mL/kgBB) Diantisipasi', default=False)
    signin_completed_at = fields.Datetime(string='Waktu Sign In')
    signin_verified_by = fields.Many2one('health.physician', string='Petugas Verifikator Sign In')

    # ==========================================================
    # 2. TIME OUT (Sebelum Insisi Kulit)
    # ==========================================================
    timeout_team_introduced = fields.Boolean(string='Seluruh Tim Operasi Memperkenalkan Diri (Nama & Peran)', default=False)
    timeout_patient_procedure_confirmed = fields.Boolean(string='Konfirmasi Verbal Nama Pasien, Tindakan, dan Posisi Insisi', default=False)
    timeout_antibiotic_prophylaxis = fields.Boolean(string='Antibiotik Profilaksis Diberikan dalam 60 Menit Terakhir', default=False)
    timeout_surgeon_review = fields.Boolean(string='Dokter Bedah Mengulas Langkah Kritis & Estimasi Durasi', default=False)
    timeout_anesthesia_review = fields.Boolean(string='Dokter Anestesi Mengulas Kekhususan Pasien & Hemodinamik', default=False)
    timeout_sterility_confirmed = fields.Boolean(string='Perawat Mengonfirmasi Sterilitas & Indikator Alat Bedah', default=False)
    timeout_imaging_displayed = fields.Boolean(string='Pencitraan Radiologi (X-Ray/CT) Ditampilkan di Layar OK', default=False)
    timeout_completed_at = fields.Datetime(string='Waktu Time Out')
    timeout_verified_by = fields.Many2one('health.physician', string='Petugas Verifikator Time Out')

    # ==========================================================
    # 3. SIGN OUT (Sebelum Menutup Luka / Pasien Meninggalkan OK)
    # ==========================================================
    signout_procedure_recorded = fields.Boolean(string='Nama Tindakan Bedah Resmi Telah Dicatat', default=False)
    signout_instrument_count_correct = fields.Boolean(string='Jumlah Kassa, Jarum, dan Instrumen Bedah Lengkap & Cocok', default=False)
    signout_specimen_labeled = fields.Boolean(string='Spesimen PA Telah Diberi Label Nama & Rekam Medis dengan Benar', default=False)
    signout_equipment_issues = fields.Boolean(string='Tidak Ada Masalah Kerusakan / Malfungsi Instrumen Bedah', default=False)
    signout_recovery_plan = fields.Boolean(string='Rencana Perawatan Pemulihan Paska Operasi Telah Diulas Bersama', default=False)
    signout_completed_at = fields.Datetime(string='Waktu Sign Out')
    signout_verified_by = fields.Many2one('health.physician', string='Petugas Verifikator Sign Out')

    overall_status = fields.Selection([
        ('pending', 'Belum Lengkap'),
        ('partial', 'Sebagian Lengkap'),
        ('completed', '100% Lengkap (Terverifikasi)'),
    ], string='Status Kelengkapan Checklist WHO', compute='_compute_overall_status', store=True)

    @api.depends(
        'signin_patient_confirmed', 'signin_site_marked', 'signin_anesthesia_check',
        'timeout_patient_procedure_confirmed', 'timeout_antibiotic_prophylaxis',
        'signout_procedure_recorded', 'signout_instrument_count_correct'
    )
    def _compute_overall_status(self):
        for rec in self:
            core_checks = [
                rec.signin_patient_confirmed, rec.signin_site_marked, rec.signin_anesthesia_check,
                rec.timeout_patient_procedure_confirmed, rec.timeout_antibiotic_prophylaxis,
                rec.signout_procedure_recorded, rec.signout_instrument_count_correct
            ]
            if all(core_checks):
                rec.overall_status = 'completed'
            elif any(core_checks):
                rec.overall_status = 'partial'
            else:
                rec.overall_status = 'pending'

    def action_complete_signin(self):
        for rec in self:
            rec.signin_completed_at = fields.Datetime.now()
            rec.signin_verified_by = rec.booking_id.anesthesiologist_id or rec.booking_id.lead_surgeon_id

    def action_complete_timeout(self):
        for rec in self:
            rec.timeout_completed_at = fields.Datetime.now()
            rec.timeout_verified_by = rec.booking_id.lead_surgeon_id

    def action_complete_signout(self):
        for rec in self:
            rec.signout_completed_at = fields.Datetime.now()
            rec.signout_verified_by = rec.booking_id.lead_surgeon_id
