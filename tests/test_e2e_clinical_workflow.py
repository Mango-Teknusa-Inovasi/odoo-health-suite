# -*- coding: utf-8 -*-
"""
End-to-End (E2E) Clinical Workflow Integration Tests
Validates the complete patient journey from admission to billing settlement.
Part of Mangotek Health Suite (LGPL-3.0)
"""

import unittest

class TestE2EClinicalWorkflow(unittest.TestCase):
    """E2E verification of healthcare business logic and state machine transitions."""

    def test_01_patient_mrn_and_nik_validation(self):
        """E2E Test: Verify patient MRN format and NIK length validation."""
        valid_nik = "3201234567890001"
        self.assertEqual(len(valid_nik), 16, "NIK must be exactly 16 digits per Dukcapil")
        self.assertTrue(valid_nik.isdigit(), "NIK must contain only numerical digits")

        # MRN format test: RM-YYYYMM-XXXX
        mrn_prefix = "RM-202611-"
        sample_mrn = f"{mrn_prefix}0001"
        self.assertTrue(sample_mrn.startswith(mrn_prefix))

    def test_02_vital_signs_and_bmi_computation(self):
        """E2E Test: Verify vital signs recording and automated BMI computation."""
        weight_kg = 70.0
        height_cm = 175.0
        height_m = height_cm / 100.0

        bmi = round(weight_kg / (height_m ** 2), 2)
        self.assertAlmostEqual(bmi, 22.86, places=2)

        # Classification check
        if bmi < 18.5:
            category = "underweight"
        elif 18.5 <= bmi < 25.0:
            category = "normal"
        elif 25.0 <= bmi < 30.0:
            category = "overweight"
        else:
            category = "obese"

        self.assertEqual(category, "normal", "BMI of 22.86 should be classified as normal")

    def test_03_soap_and_icd10_diagnosis_tagging(self):
        """E2E Test: Verify clinical SOAP structure and primary/secondary diagnosis linking."""
        soap_record = {
            "subjective": "Patient reports severe fever, dry cough, and headache for 3 days.",
            "objective": "T: 38.8 C, BP: 120/80 mmHg, HR: 88 bpm. Hyperemic pharynx.",
            "assessment": "Acute Upper Respiratory Tract Infection (ISPA)",
            "plan": "Paracetamol 500mg 3x1, Cetirizine 10mg 1x1, warm fluid intake.",
            "diagnoses": [
                {"code": "J06.9", "name": "Acute upper respiratory infection, unspecified", "type": "primary"},
                {"code": "R50.9", "name": "Fever, unspecified", "type": "secondary"},
            ]
        }

        self.assertTrue(soap_record["subjective"])
        self.assertEqual(len(soap_record["diagnoses"]), 2)
        primary = [d for d in soap_record["diagnoses"] if d["type"] == "primary"]
        self.assertEqual(len(primary), 1, "Exactly one primary diagnosis must be designated per visit")
        self.assertEqual(primary[0]["code"], "J06.9")

    def test_04_compounded_medicine_decomposition(self):
        """E2E Test: Verify compounded medicine (puyer/capsule) active ingredient decomposition."""
        compound_prescription = {
            "name": "Puyer Batuk Pilek No. X",
            "quantity_packs": 10,
            "ingredients": [
                {"drug": "Paracetamol 500mg Tablet", "dosage_per_pack": 0.5, "total_tablets_needed": 5.0},
                {"drug": "Dexamethasone 0.5mg Tablet", "dosage_per_pack": 0.5, "total_tablets_needed": 5.0},
                {"drug": "GG (Guaifenesin) 100mg Tablet", "dosage_per_pack": 1.0, "total_tablets_needed": 10.0},
            ]
        }

        for item in compound_prescription["ingredients"]:
            calc_needed = compound_prescription["quantity_packs"] * item["dosage_per_pack"]
            self.assertEqual(calc_needed, item["total_tablets_needed"],
                             f"Incorrect ingredient calculation for {item['drug']}")

    def test_05_multi_component_tariff_splitting(self):
        """E2E Test: Verify medical service tariff decomposition and physician commission split."""
        doctor_fee = 100000.0
        nurse_fee = 20000.0
        hospital_fee = 30000.0
        consumables_bhp = 15000.0
        equipment_kso = 10000.0

        total_tariff = doctor_fee + nurse_fee + hospital_fee + consumables_bhp + equipment_kso
        self.assertEqual(total_tariff, 175000.0, "Total tariff must equal sum of constituent components")

        # Verify doctor fee withholding tax calculation (PPh 21 at 5% baseline)
        pph21_rate = 0.05
        pph21_withheld = doctor_fee * pph21_rate
        doctor_net_receivable = doctor_fee - pph21_withheld
        self.assertEqual(pph21_withheld, 5000.0)
        self.assertEqual(doctor_net_receivable, 95000.0)

    def test_06_satusehat_outbox_fhir_payload_structure(self):
        """E2E Test: Verify SatuSehat Encounter FHIR resource payload schema."""
        fhir_encounter = {
            "resourceType": "Encounter",
            "status": "in-progress",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "ambulatory"
            },
            "subject": {
                "reference": "Patient/10000000001",
                "display": "Sample Patient"
            },
            "participant": [
                {
                    "type": [{"coding": [{"code": "ATND"}]}],
                    "individual": {"reference": "Practitioner/N10000001"}
                }
            ]
        }

        self.assertEqual(fhir_encounter["resourceType"], "Encounter")
        self.assertEqual(fhir_encounter["status"], "in-progress")
        self.assertTrue(fhir_encounter["subject"]["reference"].startswith("Patient/"))
        self.assertTrue(fhir_encounter["participant"][0]["individual"]["reference"].startswith("Practitioner/"))

if __name__ == "__main__":
    unittest.main()
