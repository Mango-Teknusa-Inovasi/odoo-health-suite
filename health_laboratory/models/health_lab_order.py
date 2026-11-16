# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import uuid

class HealthLabOrder(models.Model):
    _name = 'health.lab.order'
    _description = 'Laboratory Examination Order & Patient Results'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, date desc, id desc'

    name = fields.Char(string='No. Order Lab', required=True, copy=False, readonly=True, default='/')
    patient_id = fields.Many2one('health.patient', string='Pasien', required=True, tracking=True, index=True)
    medical_record_no = fields.Char(related='patient_id.medical_record_no', string='No. Rekam Medis', store=True)
    patient_age = fields.Integer(related='patient_id.age', string='Usia Pasien')
    gender = fields.Selection(related='patient_id.gender', string='Jenis Kelamin')

    date = fields.Datetime(string='Waktu Permintaan', default=fields.Datetime.now, required=True, tracking=True)
    physician_id = fields.Many2one('health.physician', string='Dokter Pengirim / DPJP', required=True, tracking=True)

    priority = fields.Selection([
        ('normal', 'Biasa (Rutin)'),
        ('cito', 'CITO / Gawat Darurat Segera (< 60 Menit)'),
    ], string='Prioritas Order', default='normal', required=True, tracking=True, index=True)

    origin_type = fields.Selection([
        ('outpatient', 'Rawat Jalan (Poliklinik)'),
        ('inpatient', 'Rawat Inap (Bangsal)'),
        ('emergency', 'IGD 24 Jam'),
        ('direct', 'Pasien Luar / Rujukan Laboratorium'),
    ], string='Asal Permintaan', default='outpatient', required=True)

    inpatient_stay_id = fields.Many2one('health.inpatient.stay', string='Episode Rawat Inap')
    emergency_triage_id = fields.Many2one('health.emergency.triage', string='Triase IGD')

    test_ids = fields.Many2many('health.lab.test', 'rel_lab_order_tests', string='Paket Pemeriksaan Lab', required=True)
    total_tariff = fields.Float(string='Total Biaya Pemeriksaan (Rp)', compute='_compute_total_tariff', store=True)

    # Specimen & Phlebotomy Tracking
    sample_barcode = fields.Char(string='No. Barcode Spesimen', readonly=True, copy=False)
    specimen_condition = fields.Selection([
        ('good', 'Baik & Cukup'),
        ('hemolyzed', 'Lisis (Hemolisis)'),
        ('lipemic', 'Lipemik (Keruh Lemak)'),
        ('icteric', 'Ikterik (Kuning Pekat)'),
        ('clotted', 'Beku (Clotted EDTA)'),
    ], string='Kondisi Sampel Fisik', default='good')

    sample_taken_time = fields.Datetime(string='Waktu Sampling (Flebotomi)')
    sample_taken_user_id = fields.Many2one('res.users', string='Petugas Flebotomi')
    sample_received_time = fields.Datetime(string='Waktu Diterima di Lab')
    sample_received_user_id = fields.Many2one('res.users', string='Penerima di Lab')

    # Result Analysis & Critical Values
    result_line_ids = fields.One2many('health.lab.result.line', 'order_id', string='Parameter & Hasil Lab')
    has_critical_value = fields.Boolean(string='Terdeteksi Nilai Kritis (Panic Value)', compute='_compute_critical_alert', store=True)

    # KARS Critical Value Telephone Readback Reporting
    critical_reported_to = fields.Char(string='Dilaporkan Kepada (DPJP / Perawat Bangsal)')
    critical_reported_time = fields.Datetime(string='Waktu Lapor Telepon')
    critical_reported_by = fields.Many2one('res.users', string='Petugas Lab Pelapor Telepon')
    critical_readback_confirmed = fields.Boolean(string='Konfirmasi Ulang (Read-Back) Selesai')
    critical_notes = fields.Text(string='Catatan Tanggapan Laporan Kritis')

    # Clinical Pathologist (Sp.PK) Specialist Verification
    analyst_id = fields.Many2one('res.users', string='Petugas Analis Lab', default=lambda self: self.env.user)
    pathologist_id = fields.Many2one('health.physician', string='Dokter Sp. Patologi Klinik (Sp.PK)')
    verified_time = fields.Datetime(string='Waktu Verifikasi Sp.PK', readonly=True)
    verification_qr_code = fields.Char(string='Token Verifikasi Digital', readonly=True, copy=False)

    state = fields.Selection([
        ('draft', 'Draft (Pengajuan)'),
        ('ordered', 'Diterbitkan (Order)'),
        ('sample_collected', 'Sampel Diambil'),
        ('sample_received', 'Sampel Diterima di Lab'),
        ('analyzed', 'Selesai Analisis (Menunggu Sp.PK)'),
        ('verified', 'Terverifikasi (Hasil Rilis)'),
        ('cancelled', 'Dibatalkan'),
    ], string='Status Order', default='draft', tracking=True, index=True)

    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)

    _sql_constraints = [
        ('health_lab_order_name_unique', 'unique(name, company_id)', 'Nomor order lab harus unik per faskes!')
    ]

    @api.depends('test_ids.tariff')
    def _compute_total_tariff(self):
        for rec in self:
            rec.total_tariff = sum(t.tariff for t in rec.test_ids)

    @api.depends('result_line_ids.is_critical')
    def _compute_critical_alert(self):
        for rec in self:
            rec.has_critical_value = any(line.is_critical for line in rec.result_line_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('health.lab.order') or '/'
        return super(HealthLabOrder, self).create(vals_list)

    def action_order(self):
        """Confirms order, generates specimen barcode, and populates result parameter lines."""
        ICP = self.env['ir.config_parameter'].sudo()
        tracking_mode = ICP.get_param('health_laboratory.tracking_mode', default='two_step')

        for rec in self:
            if not rec.test_ids:
                raise UserError(_("Pilih minimal satu paket pemeriksaan laboratorium!"))

            # Generate barcode if missing
            if not rec.sample_barcode:
                barcode_seq = self.env['ir.sequence'].next_by_code('health.lab.specimen') or str(rec.id)
                rec.sample_barcode = f"SMP-{barcode_seq}"

            # Auto-populate result lines from parameters
            existing_params = rec.result_line_ids.mapped('parameter_id')
            new_lines = []
            for test in rec.test_ids:
                for param in test.parameter_ids:
                    if param not in existing_params:
                        new_lines.append((0, 0, {
                            'test_id': test.id,
                            'parameter_id': param.id,
                            'value_numeric': 0.0,
                            'value_text': '',
                        }))
            if new_lines:
                rec.write({'result_line_ids': new_lines})

            if tracking_mode == 'direct':
                # Skip courier steps for TPMD / Solo clinics
                rec.sample_taken_time = fields.Datetime.now()
                rec.sample_taken_user_id = self.env.user.id
                rec.sample_received_time = fields.Datetime.now()
                rec.sample_received_user_id = self.env.user.id
                rec.state = 'sample_received'
            else:
                rec.state = 'ordered'

    def action_sample_collected(self):
        """Phlebotomy: sample taken at ward/clinic."""
        for rec in self:
            rec.sample_taken_time = fields.Datetime.now()
            rec.sample_taken_user_id = self.env.user.id
            rec.state = 'sample_collected'

    def action_sample_received(self):
        """Specimen reception at central laboratory."""
        for rec in self:
            rec.sample_received_time = fields.Datetime.now()
            rec.sample_received_user_id = self.env.user.id
            rec.state = 'sample_received'

    def action_analyzed(self):
        """Technical validation: Analyst finishes inputting results."""
        for rec in self:
            rec.analyst_id = self.env.user.id
            rec.state = 'analyzed'

    def action_verify_pathologist(self):
        """Clinical validation: Sp.PK signs digitally and releases certificate."""
        default_pathologist = self.env['ir.config_parameter'].sudo().get_param('health_laboratory.default_pathologist_id')
        for rec in self:
            if not rec.pathologist_id and default_pathologist:
                rec.pathologist_id = int(default_pathologist)
            if not rec.pathologist_id:
                # Find any physician with Sp.PK specialty or active doctor
                doc = self.env['health.physician'].search([('active', '=', True)], limit=1)
                if doc:
                    rec.pathologist_id = doc.id

            rec.verified_time = fields.Datetime.now()
            rec.verification_qr_code = f"LAB-VERIFIED-{rec.name}-{uuid.uuid4().hex[:8].upper()}"
            rec.state = 'verified'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'
