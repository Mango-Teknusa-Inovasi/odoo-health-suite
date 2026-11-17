# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HealthRecoveryScore(models.Model):
    _name = 'health.recovery.score'
    _description = 'Penilaian Skor Pemulihan Pasca Anestesi (PACU / Recovery Room)'
    _order = 'evaluation_time desc, id desc'

    booking_id = fields.Many2one('health.surgical.booking', string='Registrasi Operasi', required=True, ondelete='cascade')
    patient_id = fields.Many2one(related='booking_id.patient_id', string='Pasien', store=True)
    evaluation_time = fields.Datetime(string='Waktu Evaluasi', default=fields.Datetime.now, required=True)
    evaluator_id = fields.Many2one('health.physician', string='Petugas Penilai (Dokter / Perawat Anestesi)', required=True)

    scoring_type = fields.Selection([
        ('aldrete', 'Aldrete Score (Dewasa — Pasca Anestesi Umum)'),
        ('bromage', 'Bromage Score (Pasca Anestesi Spinal / Epidural)'),
        ('steward', 'Steward Score (Pediatrik — Pasien Anak)'),
    ], string='Metode Penilaian Pemulihan', required=True, default='aldrete')

    # ==========================================================
    # 1. ALDRETE SCORE (Dewasa)
    # ==========================================================
    aldrete_activity = fields.Selection([
        ('0', '0 — Tidak dapat menggerakkan satupun anggota gerak'),
        ('1', '1 — Mampu menggerakkan 2 ekstremitas'),
        ('2', '2 — Mampu menggerakkan 4 ekstremitas sesuai perintah'),
    ], string='Aktivitas Motorik', default='2')

    aldrete_respiration = fields.Selection([
        ('0', '0 — Apnea atau membutuhkan bantuan napas buatan'),
        ('1', '1 — Sesak napas / pernapasan dangkal terbatas'),
        ('2', '2 — Sanggup bernapas dalam dan batuk spontan efektif'),
    ], string='Respirasi / Pernapasan', default='2')

    aldrete_circulation = fields.Selection([
        ('0', '0 — Tekanan darah menyimpang > 50% dari pre-op'),
        ('1', '1 — Tekanan darah menyimpang 20% - 50% dari pre-op'),
        ('2', '2 — Tekanan darah menyimpang < 20% dari batas baseline pre-op'),
    ], string='Sirkulasi Tekanan Darah', default='2')

    aldrete_consciousness = fields.Selection([
        ('0', '0 — Tidak ada respon / belum sadar'),
        ('1', '1 — Bangun jika dipanggil / rangsang taktil'),
        ('2', '2 — Sadar penuh dan orientasi baik'),
    ], string='Tingkat Kesadaran', default='2')

    aldrete_color = fields.Selection([
        ('0', '0 — Sianosis / SpO2 < 90% dengan suplementasi oksigen'),
        ('1', '1 — Pucat / memerlukan O2 kanul menjaga SpO2 > 90%'),
        ('2', '2 — Kemerahan normal / SpO2 > 92% di udara ruangan'),
    ], string='Saturasi O2 / Warna Kulit', default='2')

    aldrete_total = fields.Integer(string='Total Skor Aldrete (Maks. 10)', compute='_compute_scores', store=True)

    # ==========================================================
    # 2. BROMAGE SCORE (Spinal / Regional)
    # ==========================================================
    bromage_grade = fields.Selection([
        ('0', 'Skala 0 — Gerakan penuh tungkai dan kaki (bebas fleksi lutut & pergelangan)'),
        ('1', 'Skala 1 — Tidak mampu ekstensi tungkai, hanya mampu fleksi lutut & jari kaki'),
        ('2', 'Skala 2 — Tidak mampu fleksi lutut, hanya mampu menggerakkan jari kaki'),
        ('3', 'Skala 3 — Blok motorik total, tidak ada gerakan sama sekali'),
    ], string='Skala Blok Motorik Bromage', default='0')

    # ==========================================================
    # 3. STEWARD SCORE (Pediatrik / Anak)
    # ==========================================================
    steward_consciousness = fields.Selection([
        ('0', '0 — Tidak ada respon'),
        ('1', '1 — Respon terhadap rangsangan'),
        ('2', '2 — Sadar penuh / terjaga'),
    ], string='Kesadaran Anak', default='2')

    steward_airway = fields.Selection([
        ('0', '0 — Perlu bantuan alat jalan napas'),
        ('1', '1 — Mempertahankan jalan napas mandiri'),
        ('2', '2 — Batuk efektif / menangis bebas'),
    ], string='Jalan Napas Anak', default='2')

    steward_motor = fields.Selection([
        ('0', '0 — Tidak bergerak'),
        ('1', '1 — Gerakan acak tanpa tujuan'),
        ('2', '2 — Gerakan bertujuan aktif'),
    ], string='Gerakan Motorik Anak', default='2')

    steward_total = fields.Integer(string='Total Skor Steward (Maks. 6)', compute='_compute_scores', store=True)

    # Discharge Decision
    is_cleared_for_ward = fields.Boolean(string='Aman Pindah ke Bangsal Rawat Inap', compute='_compute_scores', store=True)
    discharge_disposition = fields.Selection([
        ('ward', 'Pindah ke Bangsal Rawat Inap (KRS OK)'),
        ('icu', 'Rujuk ke Ruang Intensif (ICU / HCU / NICU)'),
        ('stay_pacu', 'Lanjut Observasi di PACU'),
    ], string='Rekomendasi Disposisi Pasien', default='ward')

    @api.depends(
        'scoring_type', 'aldrete_activity', 'aldrete_respiration', 'aldrete_circulation',
        'aldrete_consciousness', 'aldrete_color', 'bromage_grade',
        'steward_consciousness', 'steward_airway', 'steward_motor'
    )
    def _compute_scores(self):
        for rec in self:
            if rec.scoring_type == 'aldrete':
                total = (
                    int(rec.aldrete_activity or 0) +
                    int(rec.aldrete_respiration or 0) +
                    int(rec.aldrete_circulation or 0) +
                    int(rec.aldrete_consciousness or 0) +
                    int(rec.aldrete_color or 0)
                )
                rec.aldrete_total = total
                rec.steward_total = 0
                rec.is_cleared_for_ward = (total >= 8)
            elif rec.scoring_type == 'bromage':
                rec.aldrete_total = 0
                rec.steward_total = 0
                # Bromage score <= 1 means safe to move
                rec.is_cleared_for_ward = (rec.bromage_grade in ['0', '1'])
            elif rec.scoring_type == 'steward':
                total = (
                    int(rec.steward_consciousness or 0) +
                    int(rec.steward_airway or 0) +
                    int(rec.steward_motor or 0)
                )
                rec.steward_total = total
                rec.aldrete_total = 0
                rec.is_cleared_for_ward = (total >= 5)
            else:
                rec.aldrete_total = 0
                rec.steward_total = 0
                rec.is_cleared_for_ward = False
