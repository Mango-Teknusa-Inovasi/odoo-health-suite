# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class HealthEmergencyTriage(models.Model):
    _name = 'health.emergency.triage'
    _description = 'Emergency Room Triage & 24/7 IGD Episode'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'triage_priority asc, date desc, id desc'

    name = fields.Char(string='No. Triase IGD', required=True, copy=False, readonly=True, default='/')
    date = fields.Datetime(string='Waktu Masuk IGD', default=fields.Datetime.now, required=True, tracking=True, index=True)

    patient_id = fields.Many2one('health.patient', string='Pasien', required=False, tracking=True, index=True)
    medical_record_no = fields.Char(related='patient_id.medical_record_no', string='No. Rekam Medis', store=True)
    nik = fields.Char(related='patient_id.nik', string='NIK Pasien', store=True)

    physician_id = fields.Many2one('health.physician', string='Dokter Jaga IGD', tracking=True)
    nurse_id = fields.Many2one('res.users', string='Perawat Triase', default=lambda self: self.env.user)

    arrival_mode = fields.Selection([
        ('walk_in', 'Jalan Kaki Sendiri'),
        ('wheelchair', 'Kursi Roda'),
        ('stretcher', 'Brankar'),
        ('ambulance', 'Ambulans 118 / Gawat Darurat'),
    ], string='Cara Kedatangan', default='walk_in', required=True)

    arrival_reason = fields.Selection([
        ('self', 'Datang Sendiri / Sakit Mendadak'),
        ('police', 'Rujukan Polisi / Korban Kriminalitas'),
        ('doctor_referral', 'Rujukan Dokter / Klinik / Puskesmas'),
        ('workplace', 'Kecelakaan Kerja / Pabrik'),
        ('traffic_accident', 'Kecelakaan Lalu Lintas (KLL)'),
        ('other', 'Lainnya'),
    ], string='Asal Kedatangan', default='self', required=True)

    companion_name = fields.Char(string='Nama Pengantar / Keluarga')
    companion_phone = fields.Char(string='Nomor Kontak Pengantar')

    # Australasian Triage Scale (ATS) / Emergency Severity Index (ESI)
    triage_category = fields.Selection([
        ('red', 'MERAH - Resusitasi & Gawat Darurat (< 0 Menit)'),
        ('yellow', 'KUNING - Darurat Tidak Gawat (< 15 Menit)'),
        ('green', 'HIJAU - Tidak Gawat Tidak Darurat (< 60 Menit)'),
        ('black', 'HITAM - Meninggal di Tempat (DOA)'),
    ], string='Kategori Triase', required=True, tracking=True, index=True)

    triage_priority = fields.Integer(string='Prioritas Triase', compute='_compute_priority', store=True)

    # ABCD Protocol Assessment
    airway = fields.Selection([
        ('clear', 'Bebas / Paten'),
        ('threatened', 'Ancaman Sumbatan (Gurgling / Stridor)'),
        ('obstructed', 'Tersumbat Total'),
    ], string='Airway (Jalan Napas)', default='clear', required=True)

    breathing = fields.Selection([
        ('normal', 'Spontan Normal (Eupnea)'),
        ('tachypnea', 'Takipnea (>28 x/m)'),
        ('distress', 'Sesak Berat / Retraksi Otot Bantu'),
        ('apnea', 'Apnea / Napas Cuping Hidung'),
    ], string='Breathing (Pernapasan)', default='normal', required=True)

    circulation = fields.Selection([
        ('normal', 'Nadi Teraba Kuat, CRT < 2 detik'),
        ('weak', 'Nadi Cepat & Lemah (Takikardia)'),
        ('shock', 'Syok Hipovolemik / Hemoragik'),
        ('arrest', 'Henti Jantung (Cardiac Arrest)'),
    ], string='Circulation (Sirkulasi)', default='normal', required=True)

    # Disability - Glasgow Coma Scale (GCS)
    gcs_eye = fields.Integer(string='GCS Eye (1-4)', default=4)
    gcs_verbal = fields.Integer(string='GCS Verbal (1-5)', default=5)
    gcs_motor = fields.Integer(string='GCS Motor (1-6)', default=6)
    disability_gcs = fields.Integer(string='Total Skor GCS', compute='_compute_gcs', store=True)

    exposure_notes = fields.Text(string='Exposure (Jejas, Deformitas, Trauma Terbuka)')

    # Vital Signs
    systolic = fields.Integer(string='Sistolik (mmHg)', default=120)
    diastolic = fields.Integer(string='Diastolik (mmHg)', default=80)
    heart_rate = fields.Integer(string='Denyut Nadi (x/m)', default=80)
    respiratory_rate = fields.Integer(string='Laju Napas (x/m)', default=18)
    temperature = fields.Float(string='Suhu Tubuh (°C)', default=36.5)
    spo2 = fields.Float(string='Saturasi Oksigen (SpO2 %)', default=98.0)
    pain_scale = fields.Integer(string='Skala Nyeri (NRS 0-10)', default=0)

    chief_complaint = fields.Text(string='Keluhan Utama / Alasan Masuk IGD', required=True)
    triage_notes = fields.Text(string='Catatan Klinis Triase & Tindakan Resusitasi Awal')

    # Lifecycle State
    state = fields.Selection([
        ('triage', 'Triase Masuk'),
        ('resuscitation', 'Resusitasi & Stabilisasi'),
        ('observation', 'Observasi IGD'),
        ('transferred_inpatient', 'Alih Rawat Inap (Transfer)'),
        ('transferred_or', 'Kamar Operasi (OK)'),
        ('discharged', 'Pulang / Rawat Jalan'),
        ('referred', 'Rujuk ke RS Lain'),
        ('deceased', 'Meninggal Dunia'),
    ], string='Status IGD', default='triage', tracking=True, index=True)

    inpatient_stay_id = fields.Many2one('health.inpatient.stay', string='Episode Rawat Inap', readonly=True)
    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)

    _sql_constraints = [
        ('health_emergency_triage_name_unique', 'unique(name, company_id)', 'Nomor registrasi triase IGD harus unik per faskes!')
    ]

    @api.depends('triage_category')
    def _compute_priority(self):
        priority_map = {
            'red': 1,
            'yellow': 2,
            'green': 3,
            'black': 4,
        }
        for rec in self:
            rec.triage_priority = priority_map.get(rec.triage_category, 5)

    @api.depends('gcs_eye', 'gcs_verbal', 'gcs_motor')
    def _compute_gcs(self):
        for rec in self:
            rec.disability_gcs = (rec.gcs_eye or 0) + (rec.gcs_verbal or 0) + (rec.gcs_motor or 0)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('health.emergency.triage') or '/'
        return super(HealthEmergencyTriage, self).create(vals_list)

    def action_generate_mr_x(self, gender='male'):
        """Generates anonymous patient record (Mr./Mrs. X) for comatose/unidentified trauma patients."""
        for rec in self:
            seq_code = self.env['ir.sequence'].next_by_code('health.emergency.mrx') or '001'
            today_str = fields.Date.today().strftime('%Y%m%d')
            prefix = "Mr. X" if gender == 'male' else "Mrs. X"
            x_name = f"{prefix} ({today_str}-{seq_code})"

            patient = self.env['health.patient'].create({
                'name': x_name,
                'gender': gender,
                'birth_date': fields.Date.today(),
            })
            rec.patient_id = patient.id

    def action_resuscitation(self):
        for rec in self:
            rec.state = 'resuscitation'

    def action_observation(self):
        for rec in self:
            rec.state = 'observation'

    def action_transfer_to_inpatient(self, bed_id=None, physician_id=None):
        """Fast-tracks emergency patient directly into Inpatient Stay (health.inpatient.stay)."""
        self.ensure_one()
        if not self.patient_id:
            raise UserError(_("Identitas pasien belum diisi! Silakan gunakan tombol 'Generate Mr. X' jika pasien belum diketahui."))

        if not bed_id:
            # Pick first available bed in ICU if red, or general ward if yellow/green
            domain = [('state', '=', 'available')]
            if self.triage_category == 'red':
                bed = self.env['health.bed'].search([('bed_class', '=', 'icu')] + domain, limit=1)
            else:
                bed = False
            if not bed:
                bed = self.env['health.bed'].search(domain, limit=1)

            if not bed:
                raise UserError(_("Tidak ada tempat tidur rawat inap yang berstatus 'Tersedia'! Silakan sterilkan atau kosongkan ranjang terlebih dahulu."))
            bed_id = bed.id

        doc_id = physician_id or (self.physician_id.id if self.physician_id else False)
        if not doc_id:
            doc = self.env['health.physician'].search([('active', '=', True)], limit=1)
            doc_id = doc.id if doc else False

        if not doc_id:
            raise UserError(_("Dokter DPJP belum tersedia. Harap pilih Dokter DPJP."))

        # Create Inpatient Stay
        stay = self.env['health.inpatient.stay'].create({
            'patient_id': self.patient_id.id,
            'physician_id': doc_id,
            'current_bed_id': bed_id,
            'initial_diagnosis': f"[IGD Triase {self.triage_category.upper()}] {self.chief_complaint}",
            'state': 'admitted',
        })
        # Directly admit and mark bed occupied
        stay.current_bed_id.state = 'occupied'
        stay.current_bed_id.current_stay_id = stay.id

        self.inpatient_stay_id = stay.id
        self.state = 'transferred_inpatient'

        return {
            'type': 'ir.actions.act_window',
            'name': _('Episode Rawat Inap'),
            'res_model': 'health.inpatient.stay',
            'res_id': stay.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_transfer_or(self):
        for rec in self:
            rec.state = 'transferred_or'

    def action_discharge(self):
        for rec in self:
            rec.state = 'discharged'

    def action_referred(self):
        for rec in self:
            rec.state = 'referred'

    def action_deceased(self):
        for rec in self:
            rec.state = 'deceased'
