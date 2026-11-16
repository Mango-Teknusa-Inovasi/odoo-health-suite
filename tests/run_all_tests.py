#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Unit & End-to-End (E2E) Test Runner for Mangotek Health Suite (LGPL-3.0)
Discovers and executes clinical workflow tests with automatic Odoo mocking for standalone CI.
"""

import unittest
import sys
import os
from unittest.mock import MagicMock

# Mock odoo package if not available in the host/CI environment
if "odoo" not in sys.modules:
    odoo_mock = MagicMock()
    sys.modules["odoo"] = odoo_mock
    sys.modules["odoo.models"] = MagicMock()
    sys.modules["odoo.fields"] = MagicMock()
    sys.modules["odoo.api"] = MagicMock()
    sys.modules["odoo.tools"] = MagicMock()
    sys.modules["odoo.exceptions"] = MagicMock()
    sys.modules["odoo.http"] = MagicMock()

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

MODULE_TEST_PATHS = [
    "tests.test_e2e_clinical_workflow",
    "tests.test_phase1_models",
    "tests.test_phase2_models",
    "tests.test_phase3_models",
]

def run_suite():
    print("=" * 70)
    print(" 🧪 RUNNING MANGOTEK HEALTH SUITE E2E & CLINICAL WORKFLOW TESTS")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for mod_test in MODULE_TEST_PATHS:
        try:
            tests = loader.loadTestsFromName(mod_test)
            suite.addTests(tests)
            print(f"  📦 Loaded test suite: {mod_test}")
        except Exception as e:
            print(f"  ❌ Error loading {mod_test}: {e}")
            return 1

    print("\n" + "-" * 70)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    print("-" * 70)

    print(f"\n📊 RESULTS: {result.testsRun} test(s) run.")
    if result.wasSuccessful():
        print("🎉 ALL END-TO-END (E2E) CLINICAL TESTS PASSED SUCCESSFULLY!")
        print("🌟 Safe to commit per AGENTS.md Pre-Commit Protocol.")
        return 0
    else:
        print(f"🚨 FAILED: {len(result.failures)} failures, {len(result.errors)} errors.")
        print("❌ COMMIT FORBIDDEN until all E2E tests pass!")
        return 1

if __name__ == "__main__":
    sys.exit(run_suite())
