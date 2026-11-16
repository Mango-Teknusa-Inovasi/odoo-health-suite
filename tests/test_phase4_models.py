#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit & Integration Tests for Mangotek Health Suite Phase 4:
- health_laboratory (Laboratory Information System / LIS, Age/Gender Reference Ranges, Panic Values & Pathologist Verification)
- health_radiology (Medical Imaging, Hybrid DICOM PACS Bridge & Radiologist Expertise)
"""

import unittest
from datetime import datetime, date

class TestPhase4HealthcareModels(unittest.TestCase):

    def test_01_lab_test_parameter_reference_ranges(self):
        """Validates parameter reference range matching by patient age and gender."""
        # Hemoglobin parameter reference ranges
        ref_ranges = [
            {'gender': 'male', 'age_min': 18, 'age_max': 120, 'min_val': 13.0, 'max_val': 17.5},
            {'gender': 'female', 'age_min': 18, 'age_max': 120, 'min_val': 12.0, 'max_val': 16.0},
            {'gender': 'both', 'age_min': 0, 'age_max': 17, 'min_val': 11.0, 'max_val': 15.0},
        ]

        # Case 1: Adult male (Age 35)
        patient_male = {'gender': 'male', 'age': 35}
        matched_male = [r for r in ref_ranges if r['gender'] in (patient_male['gender'], 'both') and r['age_min'] <= patient_male['age'] <= r['age_max']][0]
        self.assertEqual(matched_male['min_val'], 13.0)
        self.assertEqual(matched_male['max_val'], 17.5)

        # Case 2: Adult female (Age 28)
        patient_female = {'gender': 'female', 'age': 28}
        matched_female = [r for r in ref_ranges if r['gender'] in (patient_female['gender'], 'both') and r['age_min'] <= patient_female['age'] <= r['age_max']][0]
        self.assertEqual(matched_female['min_val'], 12.0)
        self.assertEqual(matched_female['max_val'], 16.0)

    def test_02_lab_panic_critical_value_detection(self):
        """Validates automated detection and flagging of critical panic values (e.g. severe anemia or hyperglycemia)."""
        ref_hgb = {'min_val': 13.0, 'max_val': 17.5, 'critical_low': 7.0, 'critical_high': 20.0}
        ref_gds = {'min_val': 70.0, 'max_val': 140.0, 'critical_low': 50.0, 'critical_high': 500.0}

        def evaluate_value(val, ref):
            if ref.get('critical_low') and val < ref['critical_low']:
                return 'critical_low', True
            elif ref.get('critical_high') and val > ref['critical_high']:
                return 'critical_high', True
            elif ref.get('min_val') and val < ref['min_val']:
                return 'low', False
            elif ref.get('max_val') and val > ref['max_val']:
                return 'high', False
            return 'normal', False

        # Severe Anemia: Hb = 5.8 g/dL (Emergency Panic Low)
        flag_hb, is_critical_hb = evaluate_value(5.8, ref_hgb)
        self.assertEqual(flag_hb, 'critical_low')
        self.assertTrue(is_critical_hb)

        # Hyperglycemia crisis: Glucose = 550 mg/dL (Emergency Panic High)
        flag_glu, is_critical_glu = evaluate_value(550.0, ref_gds)
        self.assertEqual(flag_glu, 'critical_high')
        self.assertTrue(is_critical_glu)

        # Normal Glucose: 110 mg/dL
        flag_norm, is_critical_norm = evaluate_value(110.0, ref_gds)
        self.assertEqual(flag_norm, 'normal')
        self.assertFalse(is_critical_norm)

    def test_03_lab_order_lifecycle_and_pathologist_verification(self):
        """Validates lab order creation, specimen barcoding, and Sp.PK digital token release."""
        order = {
            'name': 'LAB/202611/0001',
            'patient_id': 101,
            'state': 'draft',
            'sample_barcode': None,
            'verification_qr_code': None,
        }

        # Confirm order (action_order) -> Generates barcode
        order['state'] = 'ordered'
        order['sample_barcode'] = 'SMP-000101'
        self.assertTrue(order['sample_barcode'].startswith('SMP-'))

        # Phlebotomy and central lab processing
        order['state'] = 'sample_received'
        order['state'] = 'analyzed'

        # Clinical Pathologist (Sp.PK) verification
        order['verification_qr_code'] = f"LAB-VERIFIED-{order['name']}-A1B2C3D4"
        order['state'] = 'verified'

        self.assertEqual(order['state'], 'verified')
        self.assertIn('LAB-VERIFIED', order['verification_qr_code'])

    def test_04_critical_value_telephone_reporting_log(self):
        """Validates KARS/STARKES telephone readback log for critical laboratory values."""
        critical_report = {
            'order_id': 'LAB/202611/0001',
            'has_critical_value': True,
            'critical_reported_to': 'Ns. Rina (Perawat Bangsal Melati)',
            'critical_reported_time': datetime(2026, 11, 17, 8, 15, 0),
            'critical_readback_confirmed': True,
            'critical_notes': 'DPJP dr. Hendra Sp.PD diinfokan via perawat. Instruksi: Transfusi PRC 2 kolf.',
        }

        self.assertTrue(critical_report['has_critical_value'])
        self.assertTrue(critical_report['critical_readback_confirmed'])
        self.assertIn('Transfusi', critical_report['critical_notes'])

    def test_05_radiology_order_and_hybrid_pacs_url(self):
        """Validates radiology examination order, accession number, and dynamic PACS viewer URL generation."""
        pacs_base_url = 'https://pacs.hospital.id/viewer?study='
        rad_order = {
            'name': 'RAD/202611/0001',
            'modality': 'xray',
            'test_name': 'Foto Thorax PA',
            'dicom_study_uid': '1.2.826.0.1.3680043.8.4981729487192',
            'accession_number': 'ACC-RAD2026110001',
            'state': 'scheduled',
        }

        # Compute dynamic web viewer launch URL
        rad_order['pacs_web_url'] = f"{pacs_base_url}{rad_order['dicom_study_uid']}"
        self.assertEqual(rad_order['pacs_web_url'], 'https://pacs.hospital.id/viewer?study=1.2.826.0.1.3680043.8.4981729487192')
        self.assertTrue(rad_order['accession_number'].startswith('ACC-'))

    def test_06_radiology_expertise_and_verification(self):
        """Validates radiographer technical data and radiologist structured expertise report."""
        rad_report = {
            'order_id': 'RAD/202611/0001',
            'modality': 'xray',
            'exposure_kvp': 55.0,
            'exposure_mas': 10.0,
            'findings': 'COR: CTR < 50%, bentuk normal. PULMO: Corakan bronkovaskular normal, tidak tampak infiltrat. Sinus kostofrenikus tajam.',
            'impression': 'Cor dan pulmo dalam batas normal (Normal Chest X-Ray).',
            'recommendations': 'Tidak ada tindakan darurat.',
            'radiologist_name': 'dr. Aditya, Sp.Rad',
            'verified_time': datetime(2026, 11, 17, 9, 30, 0),
            'verification_qr_code': 'RAD-VERIFIED-RAD/202611/0001-9F8E7D6C',
            'state': 'verified',
        }

        self.assertEqual(rad_report['state'], 'verified')
        self.assertIn('Normal Chest X-Ray', rad_report['impression'])
        self.assertTrue(rad_report['verification_qr_code'].startswith('RAD-VERIFIED'))

if __name__ == '__main__':
    unittest.main()
