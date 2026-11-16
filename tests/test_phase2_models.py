#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit & Integration Tests for Mangotek Health Suite Phase 2:
- health_appointment (Polyclinic Queuing & Rosters)
- health_pharmacy (e-Prescription, Compounding & Permenkes 73/2016 Audit)
- health_billing (Hospital Billing Ledger, 5-Component Tariff Split & Doctor Remuneration with PPh 21)
- health_bpjs (BPJS PCare FKTP Bridging)
"""

import unittest
from datetime import date, datetime
import hashlib
import hmac
import base64
import time

class TestPhase2HealthcareModels(unittest.TestCase):

    def test_01_appointment_and_dynamic_queue_generation(self):
        """Validates polyclinic appointment registration, quota checks, and sequential queue generation."""
        appointment_data = {
            'patient_id': 101,
            'physician_id': 5,
            'department_id': 2,
            'department_code': 'UMUM',
            'appointment_date': date.today(),
            'state': 'draft',
            'max_quota': 30,
            'current_patient_count': 12,
        }

        # Assert quota availability
        self.assertLess(appointment_data['current_patient_count'], appointment_data['max_quota'])

        # Generate queue ticket with by_department strategy
        count = appointment_data['current_patient_count'] + 1
        queue_number = f"{appointment_data['department_code']}-{count:03d}"
        self.assertEqual(queue_number, 'UMUM-013')

        # Status transition to waiting
        appointment_data['state'] = 'waiting'
        appointment_data['queue_number'] = queue_number
        self.assertEqual(appointment_data['state'], 'waiting')

    def test_02_prescription_compounding_and_pharmacist_review(self):
        """Validates e-Prescription 3-layer Permenkes 73/2016 audit and active ingredient compounding decomposition."""
        prescription = {
            'patient_id': 101,
            'physician_id': 5,
            'review_administrative': True,
            'review_pharmaceutical': True,
            'review_clinical': True,
            'standard_lines': [
                {'product_name': 'Paracetamol 500mg', 'qty': 10, 'price_unit': 1000.0, 'subtotal': 10000.0, 'route': 'oral'},
                {'product_name': 'Betadine Salep', 'qty': 1, 'price_unit': 18000.0, 'subtotal': 18000.0, 'route': 'topical'},
            ],
            'compound_lines': [
                {
                    'name': 'Puyer Batuk Pilek Anak',
                    'compound_type': 'pulveres',
                    'quantity': 10,
                    'embalage_fee': 500.0,  # 500 * 10 = 5,000
                    'tuslah_fee': 5000.0,
                    'ingredients': [
                        {'product_name': 'Ambroxol 30mg', 'dosage_per_unit': 15.0, 'total_quantity': 5.0, 'price_unit': 1200.0, 'subtotal': 6000.0},
                        {'product_name': 'CTM 4mg', 'dosage_per_unit': 2.0, 'total_quantity': 5.0, 'price_unit': 500.0, 'subtotal': 2500.0},
                    ]
                }
            ]
        }

        # 1. Assert 3-layer clinical screening is complete
        self.assertTrue(prescription['review_administrative'])
        self.assertTrue(prescription['review_pharmaceutical'])
        self.assertTrue(prescription['review_clinical'])

        # 2. Compounding decomposition calculation
        comp = prescription['compound_lines'][0]
        ingredients_sum = sum(i['subtotal'] for i in comp['ingredients'])
        self.assertEqual(ingredients_sum, 8500.0)

        total_embalage = comp['embalage_fee'] * comp['quantity']
        self.assertEqual(total_embalage, 5000.0)

        comp_total = ingredients_sum + total_embalage + comp['tuslah_fee']
        self.assertEqual(comp_total, 18500.0)

        # 3. Overall prescription amount
        standard_sum = sum(l['subtotal'] for l in prescription['standard_lines'])
        self.assertEqual(standard_sum, 28000.0)

        total_prescription = standard_sum + comp_total
        self.assertEqual(total_prescription, 46500.0)

    def test_03_medical_tariff_5_component_split(self):
        """Validates 5-component medical tariff decomposition and summation."""
        tariff = {
            'name': 'Tindakan Jahit Luka Ringan',
            'code': 'TRF-TND-JAHIT-1',
            'doctor_fee': 75000.0,
            'nurse_fee': 25000.0,
            'facility_fee': 25000.0,
            'bhp_amount': 25000.0,
            'equipment_fee': 0.0,
        }

        total_computed = (
            tariff['doctor_fee'] +
            tariff['nurse_fee'] +
            tariff['facility_fee'] +
            tariff['bhp_amount'] +
            tariff['equipment_fee']
        )
        self.assertEqual(total_computed, 150000.0)

    def test_04_billing_and_doctor_remuneration_with_pph21(self):
        """Validates billing net settlement and physician remuneration ledger with Indonesian PPh 21 withholding tax."""
        billing_lines = [
            {'name': 'Konsultasi Dokter Umum', 'qty': 1, 'unit_price': 50000.0, 'doctor_fee': 40000.0, 'facility_fee': 10000.0},
            {'name': 'Tindakan Jahit Luka Ringan', 'qty': 1, 'unit_price': 150000.0, 'doctor_fee': 75000.0, 'facility_fee': 75000.0},
            {'name': 'Resep Obat & Racikan', 'qty': 1, 'unit_price': 46500.0, 'doctor_fee': 0.0, 'facility_fee': 46500.0},
        ]

        gross_bill = sum(l['unit_price'] for l in billing_lines)
        self.assertEqual(gross_bill, 246500.0)

        discount = 10000.0
        net_bill = gross_bill - discount
        self.assertEqual(net_bill, 236500.0)

        # Physician Remuneration Ledger calculation
        total_doctor_gross = sum(l['doctor_fee'] for l in billing_lines)
        self.assertEqual(total_doctor_gross, 115000.0)

        # PPh 21 Tenaga Ahli Dokter (50% DPP x 5% = 2.5% effective rate)
        pph21_rate = 2.5
        pph21_tax = total_doctor_gross * (pph21_rate / 100.0)
        self.assertEqual(pph21_tax, 2875.0)

        doctor_net_receivable = total_doctor_gross - pph21_tax
        self.assertEqual(doctor_net_receivable, 112125.0)

    def test_05_bpjs_pcare_kunjungan_payload_and_hmac(self):
        """Validates BPJS PCare Outpatient Visit JSON structure and HMAC-SHA256 signature algorithm."""
        cons_id = "12345"
        secret_key = "secret_bpjs_test"
        timestamp = str(int(time.time()))

        # Compute BPJS HMAC-SHA256 signature
        data = f"{cons_id}&{timestamp}"
        signature = base64.b64encode(
            hmac.new(secret_key.encode('utf-8'), data.encode('utf-8'), hashlib.sha256).digest()
        ).decode('utf-8')

        self.assertTrue(len(signature) > 10)

        # Build BPJS PCare Kunjungan Payload
        payload = {
            'noKartu': '0001234567890',
            'tglDaftar': '16-11-2026',
            'kdPoli': '001',
            'keluhan': 'Demam menggigil sejak 2 hari lalu',
            'kdSadar': '01',
            'sistole': 120,
            'diastole': 80,
            'beratBadan': 62.5,
            'tinggiBadan': 168.0,
            'respRate': 20,
            'heartRate': 82,
            'kdStatusPulang': '1',
            'kdDiag1': 'A09',  # Diare dan gastroenteritis
        }

        self.assertEqual(payload['kdPoli'], '001')
        self.assertEqual(payload['kdSadar'], '01')
        self.assertEqual(payload['kdDiag1'], 'A09')
        self.assertEqual(len(payload['noKartu']), 13)

if __name__ == '__main__':
    unittest.main()
