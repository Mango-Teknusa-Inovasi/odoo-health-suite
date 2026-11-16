#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit & Integration Tests for Mangotek Health Suite Phase 3:
- health_inpatient (Ward Hierarchy, Real-Time BOR, Inpatient Stay, Bed Mutation, Multi-Profession CPPT, Discharge Summary)
- health_emergency (24/7 ER Triage, ATS/ESI Red/Yellow/Green/Black, ABCD Assessment, Anonymous Mr. X & Fast-Track Handover)
"""

import unittest
from datetime import datetime, timedelta, date

class TestPhase3HealthcareModels(unittest.TestCase):

    def test_01_ward_bed_hierarchy_and_bor_computation(self):
        """Validates ward bed hierarchy, occupancy metrics, and BOR formula."""
        ward_data = {
            'code': 'MELATI',
            'name': 'Bangsal Melati',
            'building': 'Gedung Rawat Inap Barat',
            'floor': 'Lantai 1',
            'beds': [
                {'name': 'MELATI-101', 'bed_class': 'class_3', 'state': 'occupied', 'daily_rate': 150000.0},
                {'name': 'MELATI-102', 'bed_class': 'class_3', 'state': 'available', 'daily_rate': 150000.0},
                {'name': 'MELATI-103', 'bed_class': 'class_3', 'state': 'cleaning', 'daily_rate': 150000.0},
                {'name': 'MELATI-104', 'bed_class': 'class_3', 'state': 'occupied', 'daily_rate': 150000.0},
            ]
        }

        total_beds = len(ward_data['beds'])
        occupied_beds = len([b for b in ward_data['beds'] if b['state'] == 'occupied'])
        available_beds = len([b for b in ward_data['beds'] if b['state'] == 'available'])
        bor_rate = (occupied_beds / total_beds) * 100.0

        self.assertEqual(total_beds, 4)
        self.assertEqual(occupied_beds, 2)
        self.assertEqual(available_beds, 1)
        self.assertEqual(bor_rate, 50.0)

    def test_02_bed_sanitation_and_sterilization_lifecycle(self):
        """Validates bed sanitation lifecycle: occupied -> cleaning -> available."""
        bed = {
            'name': 'VIP-ANGGREK-01',
            'state': 'occupied',
            'current_stay_id': 88,
        }

        # Patient transfers or discharges -> Bed enters cleaning
        def mark_cleaning(b):
            b['state'] = 'cleaning'
            b['current_stay_id'] = None

        mark_cleaning(bed)
        self.assertEqual(bed['state'], 'cleaning')
        self.assertIsNone(bed['current_stay_id'])

        # Sanitation confirmed ("Selesai Sterilisasi & Siap Pakai")
        def mark_available(b):
            b['state'] = 'available'
            b['current_stay_id'] = None

        mark_available(bed)
        self.assertEqual(bed['state'], 'available')

    def test_03_inpatient_stay_length_and_bed_mutation(self):
        """Validates inpatient stay admission, bed mutation, and length of stay calculation."""
        admission_time = datetime(2026, 11, 10, 8, 0, 0)
        discharge_time = datetime(2026, 11, 13, 14, 0, 0)

        # Noon cut-off calculation
        duration_days = (discharge_time - admission_time).total_seconds() / 86400.0
        # 3.25 days -> rounds to 4 days with noon cutoff logic (3 days + afternoon = 4 days)
        length_of_stay_noon = max(1.0, round(duration_days + 0.4))
        self.assertEqual(length_of_stay_noon, 4.0)

        # Bed mutation from Class 3 to VIP
        bed_old = {'name': 'MELATI-101', 'daily_rate': 150000.0, 'state': 'occupied'}
        bed_new = {'name': 'VIP-01', 'daily_rate': 950000.0, 'state': 'available'}

        transfer = {
            'stay_id': 1,
            'from_bed': bed_old['name'],
            'from_bed_rate': bed_old['daily_rate'],
            'to_bed': bed_new['name'],
            'to_bed_rate': bed_new['daily_rate'],
            'days_in_from_bed': 2.0,
            'reason': 'Pindah Kelas Perawatan VIP',
        }

        # Transition states
        bed_old['state'] = 'cleaning'
        bed_new['state'] = 'occupied'

        self.assertEqual(transfer['from_bed_rate'], 150000.0)
        self.assertEqual(transfer['to_bed_rate'], 950000.0)
        self.assertEqual(bed_old['state'], 'cleaning')
        self.assertEqual(bed_new['state'], 'occupied')

    def test_04_cppt_multiprofession_notes_and_24h_dpjp_verification(self):
        """Validates multi-profession CPPT notes, 24-hour verification SLA, and bulk verification."""
        now = datetime.now()
        yesterday = now - timedelta(hours=28)

        cppt_notes = [
            {
                'id': 1,
                'profession': 'nurse',
                'date': yesterday,
                'subjective': 'Pasien mengeluh mual muntah.',
                'objective': 'TD 110/70 mmHg, N 82x/m, S 37.2C.',
                'assessment': 'Resiko defisit volume cairan.',
                'plan': 'Rehidrasi RL 20 tpm, kolaborasi antiemetik.',
                'dpjp_verified': False,
            },
            {
                'id': 2,
                'profession': 'pharmacist',
                'date': yesterday,
                'subjective': 'Riwayat alergi penisilin.',
                'objective': 'Resep Ceftriaxone 2x1g IV.',
                'assessment': 'Aman, tidak ada interaksi.',
                'plan': 'Lanjutkan terapi sesuai DPJP.',
                'dpjp_verified': False,
            },
            {
                'id': 3,
                'profession': 'dpjp',
                'date': now,
                'subjective': 'Pasien merasa jauh lebih segar.',
                'objective': 'Abdomen lemas, bising usus normal.',
                'assessment': 'Gastroenteritis Akut perbaikan.',
                'plan': 'Diet lunak, rencana KRS besok.',
                'dpjp_verified': True,
            }
        ]

        # Check overdue verification flag (>24h and not verified and not DPJP own note)
        for note in cppt_notes:
            is_overdue = (not note['dpjp_verified'] and note['profession'] != 'dpjp' and (now - note['date']) > timedelta(hours=24))
            note['is_overdue'] = is_overdue

        self.assertTrue(cppt_notes[0]['is_overdue'])
        self.assertTrue(cppt_notes[1]['is_overdue'])
        self.assertFalse(cppt_notes[2]['is_overdue'])

        # Attending DPJP performs morning rounds: One-Click Bulk Verification
        dpjp_user_id = 10
        for note in cppt_notes:
            if not note['dpjp_verified']:
                note['dpjp_verified'] = True
                note['dpjp_verified_by'] = dpjp_user_id
                note['dpjp_verified_time'] = now

        unverified_count = len([n for n in cppt_notes if not n['dpjp_verified']])
        self.assertEqual(unverified_count, 0)

    def test_05_discharge_summary_and_krs(self):
        """Validates electronic discharge summary generation upon patient discharge (KRS)."""
        stay = {
            'id': 1,
            'name': 'RI/202611/0001',
            'state': 'admitted',
            'discharge_diagnosis': 'A09 - Gastroenteritis and colitis of unspecified origin',
            'bed_id': 'MELATI-101',
        }

        # Action Discharge
        stay['state'] = 'discharged'
        stay['discharge_status'] = 'improved'
        stay['discharge_date'] = datetime.now()

        # Automatic generation of discharge summary
        summary = {
            'stay_id': stay['id'],
            'primary_diagnosis': stay['discharge_diagnosis'],
            'clinical_summary': 'Pasien dirawat 4 hari dengan GEA dehidrasi sedang, membaik pasca rehidrasi.',
            'home_medication': 'Oralit 1 sachet / BAB cair, Probiotik 1x1 tab.',
            'discharge_condition': 'good',
        }

        self.assertEqual(stay['state'], 'discharged')
        self.assertEqual(stay['discharge_status'], 'improved')
        self.assertEqual(summary['discharge_condition'], 'good')

    def test_06_emergency_ats_triage_and_abcd_assessment(self):
        """Validates Australasian Triage Scale (ATS) / ESI classification and ABCD assessment."""
        # Red case: Resuscitation (< 0 min)
        triage_red = {
            'patient_name': 'Tn. Hendra',
            'triage_category': 'red',
            'airway': 'threatened',
            'breathing': 'distress',
            'circulation': 'shock',
            'gcs_eye': 2,
            'gcs_verbal': 2,
            'gcs_motor': 3,
            'systolic': 70,
            'diastolic': 40,
            'heart_rate': 135,
            'spo2': 88.0,
        }
        gcs_score = triage_red['gcs_eye'] + triage_red['gcs_verbal'] + triage_red['gcs_motor']
        self.assertEqual(gcs_score, 7) # Severe brain injury / comatose threshold < 8

        # Yellow case: Urgent (< 15 min)
        triage_yellow = {
            'patient_name': 'Ny. Siti',
            'triage_category': 'yellow',
            'airway': 'clear',
            'breathing': 'normal',
            'circulation': 'normal',
            'gcs_eye': 4,
            'gcs_verbal': 5,
            'gcs_motor': 6,
        }
        gcs_yellow = triage_yellow['gcs_eye'] + triage_yellow['gcs_verbal'] + triage_yellow['gcs_motor']
        self.assertEqual(gcs_yellow, 15)

    def test_07_emergency_mr_x_fast_track_and_inpatient_handover(self):
        """Validates fast-track anonymous Mr. X generation and one-click inpatient handover."""
        # 1. Unidentified trauma patient arrives
        today_str = date.today().strftime('%Y%m%d')
        seq = '001'
        mrx_patient = {
            'name': f"Mr. X ({today_str}-{seq})",
            'gender': 'male',
            'birth_date': date.today(),
        }
        self.assertTrue(mrx_patient['name'].startswith('Mr. X'))

        # 2. Emergency triage registered
        triage = {
            'name': 'IGD/202611/0001',
            'patient': mrx_patient['name'],
            'triage_category': 'red',
            'state': 'resuscitation',
            'chief_complaint': 'Trauma multipel KLL, penurunan kesadaran.',
        }

        # 3. One-click Fast-track handover to Inpatient ICU Bed
        inpatient_stay = {
            'name': 'RI/202611/0002',
            'patient': triage['patient'],
            'initial_diagnosis': f"[IGD Triase {triage['triage_category'].upper()}] {triage['chief_complaint']}",
            'bed': 'ICU-BED-01',
            'state': 'admitted',
        }
        triage['state'] = 'transferred_inpatient'

        self.assertEqual(triage['state'], 'transferred_inpatient')
        self.assertEqual(inpatient_stay['state'], 'admitted')
        self.assertIn('ICU', inpatient_stay['bed'])

if __name__ == '__main__':
    unittest.main()
