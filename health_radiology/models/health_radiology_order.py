# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import uuid

class HealthRadiologyOrder(models.Model):
    _name = 'health.radiology.order'
    _description = 'Radiology Examination Order & Expertise Report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, date desc, id desc'

    name = fields.Char(string='No. Order Radiologi', required=True, copy=False, readonly=True, default='/')
    patient_id = fields.Many2one('health.patient', string='Pasien', required=True, tracking=True, index=True)
    medical_record_no = fields.Char(related='patient_id.medical_record_no', string='No. Rekam Medis', store=True)
    patient_age = fields.Integer(related='patient_id.age', string='Usia Pasien')
    gender = fields.Selection(related='patient_id.gender', string='Jenis Kelamin')

    date = fields.Datetime(string='Waktu Permintaan', default=fields.Datetime.now, required=True, tracking=True)
    physician_id = fields.Many2one('health.physician', string='Dokter Pengirim / DPJP', required=True, tracking=True)

    priority = fields.Selection([
        ('normal', 'Biasa (Rutin)'),
        ('cito', 'CITO / Gawat Darurat (< 60 Menit)'),
    ], string='Prioritas Order', default='normal', required=True, tracking=True, index=True)

    origin_type = fields.Selection([
        ('outpatient', 'Rawat Jalan (Poliklinik)'),
        ('inpatient', 'Rawat Inap (Bangsal)'),
        ('emergency', 'IGD 24 Jam'),
        ('direct', 'Pasien Luar / Rujukan Radiologi'),
    ], string='Asal Permintaan', default='outpatient', required=True)

    inpatient_stay_id = fields.Many2one('health.inpatient.stay', string='Episode Rawat Inap')
    emergency_triage_id = fields.Many2one('health.emergency.triage', string='Triase IGD')

    test_id = fields.Many2one('health.radiology.test', string='Tindakan Radiologi', required=True, tracking=True)
    modality = fields.Selection(related='test_id.modality', string='Modalitas', store=True)
    tariff = fields.Float(related='test_id.tariff', string='Tarif Tindakan (Rp)', readonly=True)
    clinical_indication = fields.Text(string='Indikasi Klinis / Riwayat Singkat', required=True)

    # Technical Execution by Radiographer (Layer 1)
    radiographer_id = fields.Many2one('res.users', string='Radiografer Pemeriksa', default=lambda self: self.env.user)
    examination_time = fields.Datetime(string='Waktu Pemeriksaan / Exposure')
    projection_notes = fields.Char(string='Proyeksi Pemotretan', default='AP / PA Standar')
    exposure_kvp = fields.Float(string='Tegangan Tabung (kVp)', default=55.0)
    exposure_mas = fields.Float(string='Kuat Arus x Waktu (mAs)', default=10.0)
    contrast_used = fields.Boolean(string='Menggunakan Kontras Radiologi', default=False)
    contrast_notes = fields.Char(string='Keterangan Zat Kontras (Jenis & Dosis)')

    # Hybrid DICOM PACS Integration
    dicom_study_uid = fields.Char(string='DICOM Study Instance UID', copy=False)
    accession_number = fields.Char(string='Accession Number', copy=False)
    pacs_web_url = fields.Char(string='URL Viewer DICOM Web', compute='_compute_pacs_url', store=True)
    key_image = fields.Binary(string='Citra Utama / Key Finding (JPG/PNG)', attachment=True)
    key_image_filename = fields.Char(string='Nama File Citra')

    # Radiologist Structured Expertise (Layer 2)
    radiologist_id = fields.Many2one('health.physician', string='Dokter Spesialis Radiologi (Sp.Rad)')
    technique = fields.Char(string='Teknik Pemeriksaan', default='Foto polos tanpa kontras')
    findings = fields.Text(string='Deskripsi Temuan Radiologis / Ekspertise')
    impression = fields.Text(string='Kesan / Kesimpulan Diagnostik Radiologi')
    recommendations = fields.Text(string='Saran / Anjuran Radiologis')

    verified_time = fields.Datetime(string='Waktu Verifikasi Sp.Rad', readonly=True)
    verification_qr_code = fields.Char(string='Token Verifikasi Digital', readonly=True, copy=False)

    state = fields.Selection([
        ('draft', 'Draft (Pengajuan)'),
        ('scheduled', 'Terjadwal / Diterbitkan'),
        ('examined', 'Selesai Pemotretan (Menunggu Sp.Rad)'),
        ('verified', 'Terverifikasi (Hasil Rilis)'),
        ('cancelled', 'Dibatalkan'),
    ], string='Status Order', default='draft', tracking=True, index=True)

    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)

    _sql_constraints = [
        ('health_radiology_order_name_unique', 'unique(name, company_id)', 'Nomor order radiologi harus unik per faskes!')
    ]

    @api.depends('dicom_study_uid', 'name')
    def _compute_pacs_url(self):
        ICP = self.env['ir.config_parameter'].sudo()
        base_pacs_url = ICP.get_param('health_radiology.pacs_server_url', default='https://pacs.hospital.id/viewer?study=')
        for rec in self:
            uid = rec.dicom_study_uid or rec.accession_number or rec.name
            rec.pacs_web_url = f"{base_pacs_url}{uid}"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('health.radiology.order') or '/'
        return super(HealthRadiologyOrder, self).create(vals_list)

    def action_schedule(self):
        """Schedules examination, assigns accession number, and sets default findings template."""
        for rec in self:
            if not rec.accession_number:
                rec.accession_number = f"ACC-{rec.name.replace('/', '')}"
            if not rec.findings and rec.test_id.template_findings:
                rec.findings = rec.test_id.template_findings
            rec.state = 'scheduled'

    def action_examined(self):
        """Radiographer finishes exposure and uploads key image."""
        for rec in self:
            rec.examination_time = fields.Datetime.now()
            rec.radiographer_id = self.env.user.id
            if not rec.dicom_study_uid:
                rec.dicom_study_uid = f"1.2.826.0.1.3680043.8.{uuid.uuid4().int % 1000000000000000}"
            rec.state = 'examined'

    def action_verify_radiologist(self):
        """Radiologist Sp.Rad conducts reading, inputs impression and signs digitally."""
        default_rad = self.env['ir.config_parameter'].sudo().get_param('health_radiology.default_radiologist_id')
        for rec in self:
            if not rec.radiologist_id and default_rad:
                rec.radiologist_id = int(default_rad)
            if not rec.radiologist_id:
                doc = self.env['health.physician'].search([('active', '=', True)], limit=1)
                if doc:
                    rec.radiologist_id = doc.id

            if not rec.findings:
                raise UserError(_("Isi deskripsi temuan radiologis sebelum melakukan verifikasi hasil!"))

            rec.verified_time = fields.Datetime.now()
            rec.verification_qr_code = f"RAD-VERIFIED-{rec.name}-{uuid.uuid4().hex[:8].upper()}"
            rec.state = 'verified'

    def action_open_pacs_viewer(self):
        """Opens external DICOM web viewer in a new browser tab."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.pacs_web_url,
            'target': 'new',
        }

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'
