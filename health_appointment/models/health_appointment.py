# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime

class HealthAppointment(models.Model):
    _name = 'health.appointment'
    _description = 'Outpatient Encounter & Polyclinic Queue'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'appointment_date desc, id desc'

    name = fields.Char(string='No. Registrasi Rawat Jalan', required=True, copy=False, readonly=True, default='/')
    queue_number = fields.Char(string='Nomor Antrean', copy=False, readonly=True, tracking=True, index=True)
    appointment_date = fields.Date(string='Tanggal Pelayanan', required=True, default=fields.Date.context_today, index=True)
    appointment_time = fields.Datetime(string='Waktu Registrasi', default=fields.Datetime.now, readonly=True)

    patient_id = fields.Many2one('health.patient', string='Pasien', required=True, tracking=True, index=True)
    medical_record_no = fields.Char(related='patient_id.medical_record_no', string='No. Rekam Medis', store=True)
    nik = fields.Char(related='patient_id.nik', string='NIK Pasien', store=True)

    physician_id = fields.Many2one('health.physician', string='Dokter Pemeriksa', required=True, tracking=True, index=True)
    department_id = fields.Many2one('health.department', string='Poliklinik Tujuan', required=True, tracking=True, index=True)
    schedule_id = fields.Many2one('health.physician.schedule', string='Sesi Jadwal Praktik')

    patient_type = fields.Selection([
        ('general', 'Pasien Umum / Mandiri'),
        ('bpjs', 'BPJS Kesehatan (JKN)'),
        ('insurance', 'Asuransi Swasta / Korporasi'),
    ], string='Jenis Pembayaran / Penjamin', default='general', required=True, tracking=True)

    bpjs_card_no = fields.Char(string='No. Kartu BPJS', compute='_compute_bpjs_card_no', store=True, readonly=False)

    state = fields.Selection([
        ('draft', 'Terdaftar'),
        ('waiting', 'Menunggu Panggilan'),
        ('in_consultation', 'Sedang Diperiksa'),
        ('done', 'Selesai Pelayanan'),
        ('cancelled', 'Dibatalkan'),
    ], string='Status Antrean', default='draft', tracking=True, index=True)

    chief_complaint = fields.Char(string='Keluhan Utama / Alasan Kunjungan')
    soap_id = fields.Many2one('health.emr.soap', string='Catatan Klinis SOAP', copy=False, readonly=True)

    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)

    _sql_constraints = [
        ('health_appointment_name_unique', 'unique(name, company_id)', 'Nomor registrasi rawat jalan harus unik!')
    ]

    @api.depends('patient_id', 'patient_id.bpjs_card_no')
    def _compute_bpjs_card_no(self):
        for rec in self:
            if rec.patient_id and rec.patient_id.bpjs_card_no:
                rec.bpjs_card_no = rec.patient_id.bpjs_card_no
            elif not rec.bpjs_card_no:
                rec.bpjs_card_no = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('health.appointment') or '/'
        return super(HealthAppointment, self).create(vals_list)

    def _generate_dynamic_queue_number(self):
        """Generates sequential daily queue number according to configured strategy."""
        ICP = self.env['ir.config_parameter'].sudo()
        strategy = ICP.get_param('health_appointment.queue_strategy', default='by_department')
        custom_prefix = ICP.get_param('health_appointment.queue_custom_prefix', default='Q-')

        for rec in self:
            if rec.queue_number:
                continue

            today = rec.appointment_date or fields.Date.context_today(rec)
            domain = [
                ('appointment_date', '=', today),
                ('id', '!=', rec.id),
                ('queue_number', '!=', False),
                ('company_id', '=', rec.company_id.id)
            ]

            prefix = 'Q'
            if strategy == 'by_department':
                dept_code = rec.department_id.code or (rec.department_id.name[:4].upper() if rec.department_id.name else 'POLI')
                prefix = dept_code
                domain.append(('department_id', '=', rec.department_id.id))
            elif strategy == 'by_physician':
                doc_code = rec.physician_id.code or (rec.physician_id.name[:4].upper() if rec.physician_id.name else 'DOK')
                prefix = doc_code
                domain.append(('physician_id', '=', rec.physician_id.id))
            elif strategy == 'custom':
                prefix = custom_prefix or 'CUST'
            else:
                prefix = 'A'

            count = self.search_count(domain) + 1
            rec.queue_number = f"{prefix}-{count:03d}"

    def action_confirm(self):
        for rec in self:
            if rec.schedule_id and rec.schedule_id.max_quota > 0:
                current_count = self.search_count([
                    ('appointment_date', '=', rec.appointment_date),
                    ('schedule_id', '=', rec.schedule_id.id),
                    ('state', 'not in', ['cancelled']),
                    ('id', '!=', rec.id),
                ])
                if current_count >= rec.schedule_id.max_quota:
                    raise UserError(_("Kuota dokter %s untuk sesi ini sudah penuh (%d/%d pasien)!") % (
                        rec.physician_id.name, current_count, rec.schedule_id.max_quota
                    ))

            rec._generate_dynamic_queue_number()
            rec.state = 'waiting'

    def action_call_patient(self):
        for rec in self:
            rec.state = 'in_consultation'
            # Trigger bus message for TV digital screen if bus service is available
            try:
                self.env['bus.bus']._sendone('health_queue_channel', 'queue_call', {
                    'appointment_id': rec.id,
                    'queue_number': rec.queue_number,
                    'patient_name': rec.patient_id.name,
                    'department_name': rec.department_id.name,
                    'physician_name': rec.physician_id.name,
                })
            except Exception:
                pass

    def action_open_soap(self):
        self.ensure_one()
        if not self.soap_id:
            soap = self.env['health.emr.soap'].create({
                'patient_id': self.patient_id.id,
                'physician_id': self.physician_id.id,
                'chief_complaint': self.chief_complaint or _('Konsultasi Poli %s') % self.department_id.name,
                'company_id': self.company_id.id,
            })
            self.soap_id = soap.id

        return {
            'name': _('Clinical SOAP Consultation'),
            'type': 'ir.actions.act_window',
            'res_model': 'health.emr.soap',
            'res_id': self.soap_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'
