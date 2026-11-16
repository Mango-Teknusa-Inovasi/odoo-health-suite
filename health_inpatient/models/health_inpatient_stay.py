# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

class HealthInpatientStay(models.Model):
    _name = 'health.inpatient.stay'
    _description = 'Hospital Inpatient Episode of Care & Bed Stay'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'admission_date desc, id desc'

    name = fields.Char(string='No. Rawat Inap', required=True, copy=False, readonly=True, default='/')
    patient_id = fields.Many2one('health.patient', string='Pasien', required=True, tracking=True, index=True)
    medical_record_no = fields.Char(related='patient_id.medical_record_no', string='No. Rekam Medis', store=True)
    nik = fields.Char(related='patient_id.nik', string='NIK Pasien', store=True)

    physician_id = fields.Many2one('health.physician', string='Dokter DPJP Utama', required=True, tracking=True, index=True)
    secondary_physician_ids = fields.Many2many('health.physician', 'rel_inpatient_stay_consultants', string='Dokter Konsulen / Tim Medis')

    current_bed_id = fields.Many2one('health.bed', string='Tempat Tidur Saat Ini', required=True, tracking=True, index=True)
    ward_id = fields.Many2one('health.ward', related='current_bed_id.ward_id', string='Bangsal / Paviliun', store=True)
    bed_class = fields.Selection(related='current_bed_id.bed_class', string='Kelas Perawatan', store=True)
    daily_rate = fields.Float(related='current_bed_id.daily_rate', string='Tarif Kamar / Hari', readonly=True)

    admission_date = fields.Datetime(string='Waktu Masuk Rawat', default=fields.Datetime.now, required=True, tracking=True)
    discharge_date = fields.Datetime(string='Waktu Pulang (KRS)', tracking=True)
    length_of_stay = fields.Float(string='Lama Rawat (Hari)', compute='_compute_length_of_stay', store=True)

    initial_diagnosis = fields.Char(string='Diagnosa Masuk (Admission Dx)', required=True)
    discharge_diagnosis_id = fields.Many2one('health.diagnosis', string='Diagnosa Utama Keluar (ICD-10)', tracking=True)
    secondary_diagnosis_ids = fields.Many2many('health.diagnosis', 'rel_inpatient_stay_sec_diag', string='Diagnosa Sekunder (ICD-10)')
    procedure_ids = fields.Many2many('health.procedure', 'rel_inpatient_stay_proc', string='Tindakan / Prosedur (ICD-9 CM)')

    state = fields.Selection([
        ('draft', 'Booking / Rencana Rawat'),
        ('admitted', 'Dirawat (Aktif)'),
        ('discharged', 'Selesai Pulang (KRS)'),
        ('cancelled', 'Dibatalkan'),
    ], string='Status Rawat Inap', default='draft', tracking=True, index=True)

    discharge_status = fields.Selection([
        ('cured', 'Sembuh'),
        ('improved', 'Membaik / Atas Izin Dokter'),
        ('referred', 'Dirujuk ke RS Lain'),
        ('self_discharge', 'Pulang Paksa / APS'),
        ('deceased', 'Meninggal Dunia'),
    ], string='Status Kepulangan', tracking=True)

    bed_transfer_ids = fields.One2many('health.inpatient.transfer', 'stay_id', string='Riwayat Mutasi Kamar')
    cppt_ids = fields.One2many('health.inpatient.cppt', 'stay_id', string='Catatan CPPT Terintegrasi')
    cppt_count = fields.Integer(string='Jumlah Catatan CPPT', compute='_compute_cppt_count', store=True)
    unverified_cppt_count = fields.Integer(string='CPPT Belum Diparaf', compute='_compute_cppt_count', store=True)

    discharge_summary_ids = fields.One2many('health.inpatient.discharge.summary', 'stay_id', string='Resume Medis Pulang')
    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)

    _sql_constraints = [
        ('health_inpatient_stay_name_unique', 'unique(name, company_id)', 'Nomor rawat inap harus unik per faskes!')
    ]

    @api.depends('cppt_ids.dpjp_verified', 'cppt_ids.profession')
    def _compute_cppt_count(self):
        for rec in self:
            rec.cppt_count = len(rec.cppt_ids)
            rec.unverified_cppt_count = len(rec.cppt_ids.filtered(lambda c: not c.dpjp_verified and c.profession != 'dpjp'))

    @api.depends('admission_date', 'discharge_date')
    def _compute_length_of_stay(self):
        ICP = self.env['ir.config_parameter'].sudo()
        mode = ICP.get_param('health_inpatient.calculation_mode', default='cutoff_noon')
        for rec in self:
            if not rec.admission_date:
                rec.length_of_stay = 1.0
                continue
            end = rec.discharge_date or fields.Datetime.now()
            duration_days = (end - rec.admission_date).total_seconds() / 86400.0

            if mode == 'cutoff_noon':
                # Minimum 1 day, standard Indonesian hospital noon cutoff
                rec.length_of_stay = max(1.0, round(duration_days + 0.4))
            else:
                # Rolling 24h
                rec.length_of_stay = max(1.0, round(duration_days, 1))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('health.inpatient.stay') or '/'
        return super(HealthInpatientStay, self).create(vals_list)

    def action_admit(self):
        """Admits patient, validates bed availability, and marks bed occupied."""
        for rec in self:
            if rec.current_bed_id.state == 'occupied' and rec.current_bed_id.current_stay_id.id != rec.id:
                raise UserError(_("Tempat tidur %s saat ini sedang terisi oleh pasien lain!") % rec.current_bed_id.name)

            rec.current_bed_id.state = 'occupied'
            rec.current_bed_id.current_stay_id = rec.id
            rec.state = 'admitted'

    def action_transfer_bed(self, new_bed_id, reason="Mutasi Kelas"):
        """Transfers patient to new bed, marks previous bed cleaning, and marks new bed occupied."""
        self.ensure_one()
        new_bed = self.env['health.bed'].browse(new_bed_id)
        if new_bed.state == 'occupied':
            raise UserError(_("Tempat tidur tujuan (%s) sedang terisi!") % new_bed.name)

        old_bed = self.current_bed_id

        # Record transfer
        self.env['health.inpatient.transfer'].create({
            'stay_id': self.id,
            'from_bed_id': old_bed.id,
            'from_bed_rate': old_bed.daily_rate,
            'to_bed_id': new_bed.id,
            'to_bed_rate': new_bed.daily_rate,
            'transfer_date': fields.Datetime.now(),
            'reason': reason,
        })

        # Update bed states
        old_bed.action_mark_cleaning()
        new_bed.state = 'occupied'
        new_bed.current_stay_id = self.id
        self.current_bed_id = new_bed.id

    def action_bulk_verify_cppt(self):
        """DPJP One-Click bulk verifies all pending CPPT notes for this inpatient stay."""
        physician = self.env['health.physician'].search([('user_id', '=', self.env.user.id)], limit=1)
        for rec in self:
            unverified = rec.cppt_ids.filtered(lambda c: not c.dpjp_verified)
            for c in unverified:
                c.dpjp_verified = True
                c.dpjp_verified_time = fields.Datetime.now()
                c.dpjp_id = physician.id if physician else rec.physician_id.id

    def action_discharge(self):
        """Discharges patient (KRS), frees bed into cleaning status, and creates draft discharge summary."""
        for rec in self:
            if not rec.discharge_status:
                rec.discharge_status = 'improved'

            rec.discharge_date = fields.Datetime.now()
            if rec.current_bed_id:
                rec.current_bed_id.action_mark_cleaning()

            # Create initial electronic discharge summary if none exists
            if not rec.discharge_summary_ids and rec.discharge_diagnosis_id:
                self.env['health.inpatient.discharge.summary'].create({
                    'stay_id': rec.id,
                    'primary_diagnosis_id': rec.discharge_diagnosis_id.id,
                    'clinical_summary': f"Pasien dirawat sejak {rec.admission_date.strftime('%d-%m-%Y')} dengan keluhan {rec.initial_diagnosis}.",
                    'home_medication': 'Terapi obat pulang sesuai resep dokter.',
                })

            rec.state = 'discharged'

    def action_cancel(self):
        for rec in self:
            if rec.current_bed_id and rec.current_bed_id.current_stay_id.id == rec.id:
                rec.current_bed_id.action_mark_available()
            rec.state = 'cancelled'
