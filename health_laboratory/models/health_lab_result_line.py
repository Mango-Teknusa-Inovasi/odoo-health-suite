# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HealthLabResultLine(models.Model):
    _name = 'health.lab.result.line'
    _description = 'Laboratory Result Detail Line'
    _order = 'order_id, test_id, sequence, id'

    order_id = fields.Many2one('health.lab.order', string='Order Laboratorium', required=True, ondelete='cascade', index=True)
    patient_id = fields.Many2one('health.patient', related='order_id.patient_id', string='Pasien', store=True)
    gender = fields.Selection(related='patient_id.gender', string='Gender Pasien')
    patient_age = fields.Integer(related='patient_id.age', string='Usia Pasien')

    test_id = fields.Many2one('health.lab.test', string='Paket Pemeriksaan', required=True, index=True)
    parameter_id = fields.Many2one('health.lab.parameter', string='Parameter / Analit', required=True, index=True)
    sequence = fields.Integer(related='parameter_id.sequence', string='Urutan', store=True)
    unit = fields.Char(related='parameter_id.unit', string='Satuan')
    result_type = fields.Selection(related='parameter_id.result_type', string='Tipe Hasil')

    value_numeric = fields.Float(string='Hasil Angka')
    value_text = fields.Char(string='Hasil Teks / Kualitatif')

    reference_range_display = fields.Char(string='Nilai Rujukan Normal', compute='_compute_flag', store=True)
    flag = fields.Selection([
        ('normal', 'Normal'),
        ('low', 'Rendah (L)'),
        ('high', 'Tinggi (H)'),
        ('critical_low', 'KRITIS RENDAH (PANIC LOW)'),
        ('critical_high', 'KRITIS TINGGI (PANIC HIGH)'),
    ], string='Status Evaluasi', default='normal', compute='_compute_flag', store=True)

    is_critical = fields.Boolean(string='Nilai Kritis / Bahaya', compute='_compute_flag', store=True)
    notes = fields.Char(string='Keterangan Analis')

    @api.depends('value_numeric', 'value_text', 'parameter_id', 'order_id.patient_id.gender', 'order_id.patient_id.age')
    def _compute_flag(self):
        for rec in self:
            rec.flag = 'normal'
            rec.is_critical = False
            rec.reference_range_display = '-'

            if not rec.parameter_id:
                continue

            # Find matching reference range based on age and gender
            gender = rec.gender or 'male'
            age = rec.patient_age or 25

            ranges = rec.parameter_id.reference_ids
            matched_range = ranges.filtered(lambda r: (r.gender in (gender, 'both')) and (r.age_min_years <= age <= r.age_max_years))
            ref = matched_range[0] if matched_range else (ranges[0] if ranges else False)

            if not ref:
                continue

            if rec.result_type == 'numeric':
                rec.reference_range_display = f"{ref.min_val} - {ref.max_val} {rec.unit or ''}".strip()
                val = rec.value_numeric

                # Check Panic / Critical boundaries first
                if ref.critical_low and val < ref.critical_low:
                    rec.flag = 'critical_low'
                    rec.is_critical = True
                elif ref.critical_high and val > ref.critical_high:
                    rec.flag = 'critical_high'
                    rec.is_critical = True
                # Check normal boundaries
                elif ref.min_val and val < ref.min_val:
                    rec.flag = 'low'
                elif ref.max_val and val > ref.max_val:
                    rec.flag = 'high'
                else:
                    rec.flag = 'normal'

            else:
                rec.reference_range_display = ref.normal_text or 'Negatif'
                if rec.value_text and ref.normal_text:
                    if rec.value_text.strip().lower() != ref.normal_text.strip().lower():
                        rec.flag = 'high' # flagged abnormal
                    else:
                        rec.flag = 'normal'
