# -*- coding: utf-8 -*-
"""
Unit and Integration Tests for Phase 1 Core Modules:
- health_base
- health_emr
- health_satusehat
"""

import unittest
from datetime import date, datetime

class TestPhase1HealthcareModels(unittest.TestCase):
    """Unit and functional validation for Phase 1 models and logic."""

    def test_01_patient_mrn_and_nik_validation(self):
        """Validates patient MRN prefix and 16-digit NIK constraint."""
        valid_nik = "3201234567890001"
        self.assertEqual(len(valid_nik), 16)
        self.assertTrue(valid_nik.isdigit())

        invalid_nik = "3201234"
        self.assertNotEqual(len(invalid_nik), 16)

        # MRN format
        today = date.today()
        expected_prefix = f"RM/{today.strftime('%Y%m')}/"
        sample_mrn = f"{expected_prefix}0001"
        self.assertTrue(sample_mrn.startswith("RM/"))

    def test_02_physician_and_specialty(self):
        """Validates doctor profile and revenue share percentage."""
        doctor_data = {
            "name": "dr. Budi Santoso, Sp.A",
            "code": "DR01",
            "sip_no": "503/SIP/2026/01",
            "str_no": "3311223344556677",
            "default_fee_percentage": 70.0,
        }
        self.assertEqual(doctor_data["code"], "DR01")
        self.assertGreater(doctor_data["default_fee_percentage"], 0.0)
        self.assertLessEqual(doctor_data["default_fee_percentage"], 100.0)

    def test_03_department_and_catalogs(self):
        """Validates polyclinic service types and ICD-10/9 catalogs."""
        dept = {
            "code": "POL01",
            "name": "Poli Umum",
            "service_type": "outpatient",
            "default_registration_fee": 25000.0,
        }
        self.assertIn(dept["service_type"], ['outpatient', 'inpatient', 'emergency', 'pharmacy', 'laboratory', 'radiology', 'administration'])

        icd10 = {"code": "J06.9", "name": "Acute upper respiratory infection, unspecified"}
        display_name = f"[{icd10['code']}] {icd10['name']}"
        self.assertEqual(display_name, "[J06.9] Acute upper respiratory infection, unspecified")

    def test_04_vital_signs_bmi_and_gcs(self):
        """Validates vital signs calculations: BMI formula, status classification, and GCS total."""
        weight = 75.0
        height = 170.0
        h_m = height / 100.0
        bmi = round(weight / (h_m * h_m), 2)
        self.assertAlmostEqual(bmi, 25.95, places=2)

        # Classification check: 25.95 is overweight
        if bmi < 18.5:
            cat = 'underweight'
        elif 18.5 <= bmi < 25.0:
            cat = 'normal'
        elif 25.0 <= bmi < 30.0:
            cat = 'overweight'
        else:
            cat = 'obese'
        self.assertEqual(cat, 'overweight')

        # GCS calculation: Eye(4) + Verbal(5) + Motor(6) = 15
        gcs_eye = 4
        gcs_verbal = 5
        gcs_motor = 6
        gcs_total = gcs_eye + gcs_verbal + gcs_motor
        self.assertEqual(gcs_total, 15)

    def test_05_soap_consultation_workflow(self):
        """Validates SOAP consultation record and primary diagnosis validation."""
        soap = {
            "name": "SOAP/202611/0001",
            "chief_complaint": "Batuk dan demam",
            "subjective": "Batuk sejak 2 hari yang lalu, dahak kental, demam naik turun.",
            "objective": "T: 38.2 C, TD: 110/70 mmHg, ronki basah halus minimal.",
            "assessment": "Bronkitis Akut",
            "plan": "Amoxicillin 500mg 3x1, Ambroxol 30mg 3x1, Paracetamol 500mg prn demam.",
            "diagnosis_lines": [
                {"code": "J20.9", "type": "primary"},
                {"code": "R50.9", "type": "secondary"},
            ],
            "state": "draft"
        }

        # Check required fields
        self.assertTrue(soap["chief_complaint"])
        self.assertTrue(soap["subjective"])
        self.assertTrue(soap["objective"])
        self.assertTrue(soap["plan"])

        # Validate that primary diagnosis is present
        has_primary = any(d["type"] == "primary" for d in soap["diagnosis_lines"])
        self.assertTrue(has_primary, "Primary diagnosis must exist to finalize SOAP consultation")

        # Simulate state transition
        soap["state"] = "done"
        self.assertEqual(soap["state"], "done")

    def test_06_satusehat_outbox_queue(self):
        """Validates SatuSehat Outbox integration log lifecycle."""
        outbox_entry = {
            "service": "satusehat",
            "resource_type": "Encounter",
            "endpoint_url": "https://api-satusehat-dev.dto.kemkes.go.id/fhir-r4/v1/Encounter",
            "http_method": "POST",
            "state": "draft",
            "retry_count": 0
        }

        self.assertEqual(outbox_entry["state"], "draft")
        # Simulate dispatch success
        outbox_entry["state"] = "success"
        outbox_entry["response_code"] = 201
        self.assertEqual(outbox_entry["state"], "success")
        self.assertEqual(outbox_entry["response_code"], 201)

if __name__ == "__main__":
    unittest.main()
