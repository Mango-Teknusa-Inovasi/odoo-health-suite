# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class HealthSurgicalBooking(models.Model):
    _name = 'health.surgical.booking'
    _description = 'Jadwal Pembedahan & Prosedur Kamar Operasi (IBS/VK)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'schedule_start desc, id desc'

    name = fields.Char(string='No. Registrasi Operasi', required=True, copy=False, readonly=True, default=lambda self: _('Baru'))
    patient_id = fields.Many2one('health.patient', string='Pasien', required=True, tracking=True)
    patient_mrn = fields.Char(related='patient_id.mrn', string='No. Rekam Medis', store=True)
    patient_nik = fields.Char(related='patient_id.nik', string='NIK Pasien')
    patient_gender = fields.Selection(related='patient_id.gender', string='Jenis Kelamin')
    patient_age = fields.Integer(related='patient_id.age', string='Usia (Tahun)')

    inpatient_stay_id = fields.Many2one('health.inpatient.stay', string='Admisi Rawat Inap Asal', help='Kamar rawat inap pasien sebelum masuk kamar operasi')
    room_id = fields.Many2one('health.operating.room', string='Kamar Operasi / VK', required=True, tracking=True)
    room_type = fields.Selection(related='room_id.room_type', string='Tipe Fasilitas Ruangan', store=True)
    procedure_id = fields.Many2one('health.surgical.procedure', string='Rencana Tindakan Pembedahan', required=True, tracking=True)
    icd9_id = fields.Many2one(related='procedure_id.icd9_id', string='Kode ICD-9 CM', store=True)

    urgency = fields.Selection([
        ('elective', 'Operasi Terjadwal / Elektif'),
        ('cito', 'Operasi Emergency / Cito'),
    ], string='Tingkat Urgensi', required=True, default='elective', tracking=True)

    schedule_start = fields.Datetime(string='Rencana Waktu Mulai', required=True, tracking=True)
    schedule_end = fields.Datetime(string='Rencana Waktu Selesai', required=True, tracking=True)
    actual_start = fields.Datetime(string='Waktu Mulai Aktual (Insisi)', readonly=True)
    actual_end = fields.Datetime(string='Waktu Selesai Aktual (Jahit Selesai)', readonly=True)

    # Multi-Disciplinary Surgical Team
    lead_surgeon_id = fields.Many2one('health.physician', string='Dokter Operator Utama (DPJP)', required=True, tracking=True)
    assistant_surgeon_id = fields.Many2one('health.physician', string='Asisten Bedah')
    anesthesiologist_id = fields.Many2one('health.physician', string='Dokter Spesialis Anestesi (Sp.An)')
    pediatrician_id = fields.Many2one('health.physician', string='Dokter Spesialis Anak (Sp.A)', help='Wajib untuk Sectio Caesarea / Bayi berisiko')
    scrub_nurse_id = fields.Many2one('health.nurse', string='Perawat Instrumen (Scrub Nurse)')
    circulating_nurse_id = fields.Many2one('health.nurse', string='Perawat Sirkuler (Omloop)')

    # Clinical Operative Report
    preop_diagnosis_id = fields.Many2one('health.icd10', string='Diagnosa Pre-Operatif', required=True)
    postop_diagnosis_id = fields.Many2one('health.icd10', string='Diagnosa Post-Operatif')
    surgical_technique = fields.Text(string='Laporan Prosedur & Teknik Pembedahan')
    tissue_excised = fields.Char(string='Jaringan yang Dieksisi / Diambil')
    send_to_pa = fields.Boolean(string='Kirim Spesimen ke Patologi Anatomi (PA)', default=False)
    implant_serial = fields.Char(string='Nomor Seri Implan / Protesis')
    blood_loss_ml = fields.Integer(string='Estimasi Perdarahan (mL)', default=0)

    # State & Flow
    state = fields.Selection([
        ('draft', 'Pengajuan Jadwal'),
        ('scheduled', 'Terkonfirmasi'),
        ('in_progress', 'Operasi Berlangsung'),
        ('recovery', 'Pemulihan PACU'),
        ('done', 'Selesai & Keluar OK'),
        ('cancelled', 'Dibatalkan'),
    ], string='Status Operasi', default='draft', tracking=True)

    # Billing & Financials
    billing_id = fields.Many2one('health.billing.ledger', string='Faktur Billing Pasien', readonly=True)
    company_id = fields.Many2one('res.company', string='Rumah Sakit', default=lambda self: self.env.company)

    # Related Clinical Sub-Records
    checklist_ids = fields.One2many('health.surgical.checklist', 'booking_id', string='Checklist Keselamatan WHO')
    checklist_count = fields.Integer(string='Jumlah Checklist', compute='_compute_sub_counts')
    anesthesia_record_ids = fields.One2many('health.anesthesia.record', 'booking_id', string='Catatan Anestesi')
    recovery_score_ids = fields.One2many('health.recovery.score', 'booking_id', string='Skor Pemulihan PACU')
    partus_record_ids = fields.One2many('health.partus.record', 'booking_id', string='Catatan Persalinan VK')

    def _compute_sub_counts(self):
        for rec in self:
            rec.checklist_count = len(rec.checklist_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Baru')) == _('Baru'):
                vals['name'] = self.env['ir.sequence'].next_by_code('health.surgical.booking') or _('SURG/%s') % fields.Date.today().strftime('%Y%m%d')
        return super().create(vals_list)

    @api.constrains('schedule_start', 'schedule_end')
    def _check_schedule_time(self):
        for rec in self:
            if rec.schedule_end <= rec.schedule_start:
                raise ValidationError(_("Waktu perkiraan selesai operasi harus lebih besar daripada waktu mulai!"))

    def action_confirm_schedule(self):
        for rec in self:
            rec.state = 'scheduled'

    def action_start_surgery(self):
        for rec in self:
            rec.state = 'in_progress'
            rec.actual_start = fields.Datetime.now()
            if rec.room_id:
                rec.room_id.state = 'in_use'
            # Automatically create WHO checklist if none exists
            if not rec.checklist_ids:
                self.env['health.surgical.checklist'].create({
                    'booking_id': rec.id,
                    'patient_id': rec.patient_id.id,
                })

    def action_transfer_to_pacu(self):
        for rec in self:
            rec.state = 'recovery'
            rec.actual_end = fields.Datetime.now()
            if rec.room_id:
                rec.room_id.state = 'cleaning'

    def action_complete_surgery(self):
        for rec in self:
            rec.state = 'done'
            if rec.room_id and rec.room_id.state == 'cleaning':
                rec.room_id.state = 'available'
            # Check or create billing ledger entry
            rec._create_surgical_billing()

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'
            if rec.room_id and rec.room_id.state == 'in_use':
                rec.room_id.state = 'available'

    def _create_surgical_billing(self):
        self.ensure_one()
        if hasattr(self.env['health.billing.ledger'], 'create'):
            # Check if ledger exists for patient stay or patient
            ledger = self.env['health.billing.ledger'].search([
                ('patient_id', '=', self.patient_id.id),
                ('state', '=', 'draft')
            ], limit=1)
            if not ledger:
                ledger = self.env['health.billing.ledger'].create({
                    ('inpatient_stay_id' if hasattr(self.env['health.billing.ledger'], 'inpatient_stay_id') and self.inpatient_stay_id else 'patient_id'): (self.inpatient_stay_id.id if self.inpatient_stay_id else self.patient_id.id),
                    'patient_id': self.patient_id.id,
                    'service_type': 'inpatient' if self.inpatient_stay_id else 'outpatient',
                })
            self.billing_id = ledger.id
