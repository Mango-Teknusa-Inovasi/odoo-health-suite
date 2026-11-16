# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HealthTariffTemplate(models.Model):
    _name = 'health.tariff.template'
    _description = 'Medical Service Tariff Master & Component Split'
    _order = 'department_id, name'

    name = fields.Char(string='Nama Tindakan / Layanan Medis', required=True, index=True)
    code = fields.Char(string='Kode Tarif', index=True)
    procedure_id = fields.Many2one('health.procedure', string='Kode Prosedur (ICD-9 CM)')
    department_id = fields.Many2one('health.department', string='Poliklinik / Departemen Terkait')

    # Indonesian 5-Component Decomposition
    doctor_fee = fields.Float(string='Jasa Medis Dokter (Rp)', default=0.0)
    nurse_fee = fields.Float(string='Jasa Paramedis / Perawat (Rp)', default=0.0)
    facility_fee = fields.Float(string='Jasa Sarana & Fasilitas (Rp)', default=0.0)
    bhp_amount = fields.Float(string='Biaya Bahan Habis Pakai (BHP)', default=0.0)
    equipment_fee = fields.Float(string='Sewa Alat Medis / KSO (Rp)', default=0.0)

    total_amount = fields.Float(string='Total Tarif Pasien (Rp)', compute='_compute_total_amount', store=True)
    active = fields.Boolean(string='Aktif', default=True)
    company_id = fields.Many2one('res.company', string='Fasilitas Kesehatan', default=lambda self: self.env.company)

    @api.depends('doctor_fee', 'nurse_fee', 'facility_fee', 'bhp_amount', 'equipment_fee')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = (
                rec.doctor_fee +
                rec.nurse_fee +
                rec.facility_fee +
                rec.bhp_amount +
                rec.equipment_fee
            )
