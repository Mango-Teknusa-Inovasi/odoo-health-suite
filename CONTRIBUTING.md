# Contributing to Mangotek Health Suite

Thank you for your interest in contributing to **Mangotek Health Suite**! As an open-source, mission-critical healthcare platform, we welcome contributions from developers, clinicians, clinical pharmacists, and healthcare IT administrators worldwide.

---

## 1. Development Environment & Setup

We recommend running Mangotek Health Suite via the official Docker environment:

```bash
# Clone the repository
git clone https://github.com/Mango-Teknusa-Inovasi/odoo-health.git
cd odoo-health

# Ensure dependencies are loaded via docker-compose
docker compose up -d
```

---

## 2. Contribution Workflow

1. **Fork the Repository**: Create your own fork on GitHub.
2. **Create a Feature Branch**:
   ```bash
   git checkout -b feat/18.0-encounter-triage
   ```
3. **Commit Guidelines**: We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
   - `feat(health_emr): add pediatric developmental milestone tracker`
   - `fix(health_billing): prevent rounding discrepancy on multi-tier tariff split`
   - `docs(brandkit): update banner layout specs`
   - `test(health_pharmacy): add unit test for compounded medicine FEFO lot picking`
4. **Mandatory Pre-Commit Testing (Zero Commit Without Passing E2E)**:
   Contributors and agents **MUST** run and pass both the end-to-end clinical workflow suite and the store compliance audit before creating any git commit:
   ```bash
   # 1. Run End-to-End (E2E) & Unit Test Suite
   python tests/run_all_tests.py

   # 2. Run Odoo Apps Store Compliance Validator
   python scripts/validate_apps_store.py
   ```
   *Commits containing broken clinical flows or failing test suites will be rejected automatically.*
5. **Submit a Pull Request**:
   - Reference any related GitHub issue numbers.
   - Include test results and visual screenshots for UI changes.

---

## 3. Coding & Style Conventions

- **Python**: Follow PEP 8 and official [Odoo Coding Guidelines](https://www.odoo.com/documentation/18.0/developer/reference/backend/guidelines.html).
- **XML / Views**: Consistent 4-space indentation. Maintain semantic tag nesting (`<record>`, `<form>`, `<sheet>`, `<notebook>`, `<page>`).
- **Translations**: Always wrap user-facing strings in `_("...")` for internationalization (`i18n`).
- **Anti-Slop Cleanliness**: Adhere strictly to the guidelines set in `AGENTS.md` (no generic AI filler comments, no phantom imports).

---

## 4. Code of Conduct

All contributors are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). Please report unacceptable behavior to `billing@ppti.me`.
