# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    health_is_medicine = fields.Boolean(
        string='Produk Farmasi / Obat & Alkes',
        default=False,
        help='Centang jika produk ini merupakan sediaan farmasi, obat, atau alat kesehatan habis pakai.'
    )
    health_dosage_form = fields.Selection([
        ('tablet', 'Tablet / Kaplet'),
        ('capsule', 'Kapsul'),
        ('syrup', 'Sirup / Suspensi'),
        ('powder', 'Serbuk / Puyer'),
        ('ointment', 'Salep / Gel / Krim'),
        ('injection', 'Injeksi / Infus'),
        ('drop', 'Tetes Mata / Telinga'),
        ('inhaler', 'Inhaler / Nebulizer'),
        ('suppository', 'Supositoria'),
        ('other', 'Lainnya'),
    ], string='Bentuk Sediaan Farmasi', default='tablet')

    health_composition = fields.Char(
        string='Kandungan Zat Aktif & Dosis',
        help='cth. Paracetamol 500mg, Amoxicillin Trihydrate 500mg'
    )
    health_standard_signa = fields.Char(
        string='Default Aturan Pakai (Signa)',
        help='cth. 3 x 1 tablet sesudah makan'
    )
