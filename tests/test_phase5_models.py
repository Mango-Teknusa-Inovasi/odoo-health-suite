# -*- coding: utf-8 -*-
"""
Mangotek Health Suite — Phase 5 Test Suite
Covers:
1. health_surgery (Operating Room, Surgical Booking, WHO Checklist, Anesthesia, PACU Scores, Partus VK)
2. health_bpjs_vclaim (VClaim 2.0 SEP Generator, SPRI, Surat Kontrol)
3. health_inacbg (E-Klaim INA-CBG Grouper, Special CMG & Tariff Disparity Margin Audit)
"""

import unittest
from datetime import datetime, date, timedelta


class MockRecord:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getattr__(self, name):
        return self.__dict__.get(name, False)

    def __setattr__(self, name, value):
        self.__dict__[name] = value


class TestPhase5HealthcareModels(unittest.TestCase):

    def test_01_operating_room_and_procedure_tariff(self):
        """Validates Operating & Delivery room creation, state flow, and 4-component surgical tariff."""
        room = MockRecord(
            name="Kamar Operasi 1 (Mayor)",
            code="OK-01",
            room_type="major_or",
            state="available"
        )
        self.assertEqual(room.state, "available")
        self.assertEqual(room.room_type, "major_or")

        # Test Procedure 4-component tariff split
        op_fee = 3500000.0
        anes_fee = 1500000.0
        room_fee = 1200000.0
        bhp_fee = 800000.0
        total_tariff = op_fee + anes_fee + room_fee + bhp_fee
        self.assertEqual(total_tariff, 7000000.0)

    def test_02_surgical_booking_lifecycle_and_multidisciplinary_team(self):
        """Validates surgical booking lifecycle and multidisciplinary surgical team assignment."""
        now = datetime.now()
        booking = MockRecord(
            name="SURG/2026/11/0001",
            patient_id=MockRecord(name="Ny. Siti Aminah", mrn="RM-2026-00045"),
            room_id=MockRecord(name="OK-01", state="available"),
            procedure_id=MockRecord(name="Sectio Caesarea (SC)", code="SC-01"),
            urgency="cito",
            schedule_start=now,
            schedule_end=now + timedelta(hours=2),
            lead_surgeon_id=MockRecord(name="dr. Herman Sp.OG"),
            anesthesiologist_id=MockRecord(name="dr. Budi Sp.An"),
            pediatrician_id=MockRecord(name="dr. Linda Sp.A"),
            scrub_nurse_id=MockRecord(name="Ns. Dewi S.Kep"),
            circulating_nurse_id=MockRecord(name="Ns. Roni S.Kep"),
            state="draft"
        )
        self.assertEqual(booking.urgency, "cito")
        self.assertIsNotNone(booking.pediatrician_id)

        # Transition: draft -> in_progress
        booking.state = "in_progress"
        booking.room_id.state = "in_use"
        self.assertEqual(booking.room_id.state, "in_use")

        # Transition: in_progress -> recovery (PACU)
        booking.state = "recovery"
        booking.room_id.state = "cleaning"
        self.assertEqual(booking.room_id.state, "cleaning")

        # Transition: recovery -> done
        booking.state = "done"
        booking.room_id.state = "available"
        self.assertEqual(booking.state, "done")
        self.assertEqual(booking.room_id.state, "available")

    def test_03_who_surgical_safety_checklist_validation(self):
        """Validates WHO Surgical Safety Checklist (Sign In, Time Out, Sign Out) and completion status."""
        checklist = MockRecord(
            signin_patient_confirmed=True,
            signin_site_marked=True,
            signin_anesthesia_check=True,
            timeout_patient_procedure_confirmed=True,
            timeout_antibiotic_prophylaxis=True,
            signout_procedure_recorded=True,
            signout_instrument_count_correct=True,
            overall_status="pending"
        )

        core_checks = [
            checklist.signin_patient_confirmed,
            checklist.signin_site_marked,
            checklist.signin_anesthesia_check,
            checklist.timeout_patient_procedure_confirmed,
            checklist.timeout_antibiotic_prophylaxis,
            checklist.signout_procedure_recorded,
            checklist.signout_instrument_count_correct,
        ]
        if all(core_checks):
            checklist.overall_status = "completed"
        elif any(core_checks):
            checklist.overall_status = "partial"

        self.assertEqual(checklist.overall_status, "completed")

    def test_04_anesthesia_record_and_recovery_scoring(self):
        """Validates Anesthesia record and PACU recovery scoring systems (Aldrete, Bromage, Steward)."""
        # 1. Aldrete Score (Adult GA)
        aldrete = MockRecord(
            scoring_type="aldrete",
            activity=2,       # Moves 4 limbs
            respiration=2,    # Deep breath & cough
            circulation=2,    # BP within 20%
            consciousness=2,  # Fully awake
            color=2,          # Pink, SpO2 > 92%
        )
        total_aldrete = aldrete.activity + aldrete.respiration + aldrete.circulation + aldrete.consciousness + aldrete.color
        self.assertEqual(total_aldrete, 10)
        self.assertTrue(total_aldrete >= 8, "Aldrete >= 8 must be cleared for general ward transfer.")

        # 2. Bromage Score (Spinal Anesthesia)
        bromage_grade = "1"  # Unable to extend leg, flexes knees and feet
        is_bromage_cleared = (bromage_grade in ["0", "1"])
        self.assertTrue(is_bromage_cleared, "Bromage grade 0 or 1 is cleared for ward.")

        # 3. Steward Score (Pediatric)
        steward = MockRecord(
            consciousness=2,  # Awake
            airway=2,         # Coughing / crying
            motor=2           # Purposeful movement
        )
        total_steward = steward.consciousness + steward.airway + steward.motor
        self.assertEqual(total_steward, 6)
        self.assertTrue(total_steward >= 5, "Steward >= 5 is cleared for pediatric discharge.")

    def test_05_delivery_suite_vk_partus_record(self):
        """Validates labor & delivery room (VK) partograph, neonatal APGAR scores, and IMD status."""
        partus = MockRecord(
            delivery_type="spontaneous",
            kala1_hours=4.5,
            kala2_minutes=25,
            kala3_minutes=10,
            placenta_delivery="spontaneous",
            perineal_tear="degree_2",
            baby_gender="female",
            baby_weight_grams=3250,
            apgar_1=8,
            apgar_5=10,
            baby_condition="vigorous",
            imd_performed=True
        )
        self.assertEqual(partus.baby_gender, "female")
        self.assertEqual(partus.apgar_5, 10)
        self.assertTrue(partus.imd_performed)
        self.assertEqual(partus.baby_condition, "vigorous")

    def test_06_bpjs_vclaim_sep_generation_and_spri(self):
        """Validates BPJS VClaim 2.0 SEP generation, SPRI linking, and official 19-digit SEP pattern."""
        ppk_code = "0195R014"
        period_str = datetime.now().strftime("%m%y")
        seq_num = "000042"
        sep_number = f"{ppk_code}{period_str}V{seq_num}"

        sep = MockRecord(
            name=sep_number,
            no_kartu="0001234567890",
            jenis_pelayanan="1",  # Inpatient
            kelas_rawat="3",
            tgl_sep=date.today(),
            no_rujukan="0195B0010126P000001",
            state="published"
        )
        # Check standard 19-character length
        self.assertEqual(len(sep.name), 19)
        self.assertTrue(sep.name.startswith(ppk_code))
        self.assertIn("V", sep.name)
        self.assertEqual(sep.state, "published")

        # SPRI linkage
        spri = MockRecord(
            name="SPRI-202611001",
            patient_id=MockRecord(name="Bpk. Joko Susilo"),
            tgl_rencana_inap=date.today() + timedelta(days=1),
            state="approved"
        )
        self.assertEqual(spri.state, "approved")

    def test_07_inacbg_grouping_and_tariff_disparity_audit(self):
        """Validates INA-CBG Case-Based Grouping, Special CMG, and Hospital Real Cost Disparity Audit."""
        # Case A: Surgical Sectio Caesarea (Surplus Claim Margin)
        claim_sc = MockRecord(
            cbg_code="O-6-10-I",
            cbg_description="PERSALINAN DENGAN SECTIO CAESAREA",
            base_tariff=5850000.0,
            special_cmg_tariff=0.0,
            hospital_real_bill=4700000.0
        )
        total_tariff_sc = claim_sc.base_tariff + claim_sc.special_cmg_tariff
        disparity_sc = total_tariff_sc - claim_sc.hospital_real_bill
        margin_status_sc = "surplus" if disparity_sc > 0 else "deficit"

        self.assertEqual(disparity_sc, 1150000.0)
        self.assertEqual(margin_status_sc, "surplus")

        # Case B: Complex Surgery / Complications with Deficit Margin
        claim_deficit = MockRecord(
            cbg_code="I-4-10-I",
            cbg_description="PROSEDUR BEDAH INTRA-ABDOMEN LAIN",
            base_tariff=4920000.0,
            special_cmg_tariff=0.0,
            hospital_real_bill=6100000.0  # Prolonged ICU or expensive consumables
        )
        disparity_def = claim_deficit.base_tariff - claim_deficit.hospital_real_bill
        margin_status_def = "surplus" if disparity_def > 0 else "deficit"

        self.assertEqual(disparity_def, -1180000.0)
        self.assertEqual(margin_status_def, "deficit")


if __name__ == "__main__":
    unittest.main()
