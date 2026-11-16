# Security & Patient Data Protection Policy (SECURITY.md)

> **Mandatory Security Standards for Healthcare Data, Medical Records & Financial Transactions**  
> **Maintained by:** Mangotek Security Team · **Security Contact:** `billing@ppti.me`

---

## 1. Healthcare Security Mission & Compliance

**Mangotek Health Suite** processes Protected Health Information (PHI), medical clinical notes, and financial hospital transactions. Protecting the confidentiality, integrity, and availability of this data is paramount.

Our security architecture complies with:
- **Indonesian Ministry of Health Regulation PMK No. 24 of 2022** concerning Electronic Medical Records (RME).
- **Indonesian Personal Data Protection Law (UU PDP No. 27 of 2022)**.
- **HL7 FHIR & OpenID Connect / OAuth2 Security Standards**.
- **OWASP Top 10 Security Guidelines** for Web Applications and APIs.

---

## 2. Core Security Controls

### A. Role-Based Access Control (RBAC) & Segregation of Duties
1. **Clinical Segregation:** Receptionists cannot view clinical SOAP diagnoses; general doctors cannot alter pharmacy inventory valuation; cashiers cannot modify medical prescriptions.
2. **Access Rights Verification:** All models declared in `models/` must have strictly defined read/write/create/unlink permissions in `security/ir.model.access.csv`.
3. **Record Rules (Multi-Branch Isolation):** Strict multi-company rules ensure medical records from one hospital or clinic branch cannot be accessed by another unless an explicit medical referral is authorized.

### B. Audit Trail & Access Logging
- Core clinical models (`health.encounter`, `health.emr.soap`, `health.prescription`) inherit `mail.thread` to track changes with timestamps, user IDs, and field diffs.
- Sensitive diagnostic changes require active tracking (`tracking=True`).

### C. Prevention of Injection & Remote Code Execution
- **SQL Injection:** Raw string formatting (`f"..."` or `+`) inside `self.env.cr.execute()` is strictly forbidden. All SQL executions must pass parameters via tuples.
- **Cross-Site Scripting (XSS):** User-facing templates must escape inputs. `static/description/index.html` strictly bans `<script>` tags.

### D. Credential & Secret Management
- API tokens (SatuSehat Client Secret, BPJS Consumer Secret, QRIS Merchant Keys) must never be hardcoded in Python files or Git history.
- Credentials must be stored in encrypted system parameters (`ir.config_parameter`) or injected via container environment variables.

---

## 3. Reporting a Vulnerability

We deeply appreciate the efforts of security researchers and community members who identify potential vulnerabilities.

### Responsible Disclosure Process
1. **Do NOT open public GitHub issues** for security vulnerabilities.
2. Submit a confidential report directly to our security team at:  
   📧 **`billing@ppti.me`**
3. In your report, please include:
   - Module name and file path(s) involved.
   - Detailed step-by-step proof-of-concept (PoC) or reproduction steps.
   - Assessment of potential impact (e.g. data leak, privilege escalation, bypass of billing).

### Response SLA
| Severity | Initial Triage & Acknowledgment | Target Fix & Advisory Release |
|:---|:---|:---|
| **Critical** (PHI exposure, remote code execution) | Within 24 hours | Within 72 hours |
| **High** (Privilege escalation, billing tampering) | Within 48 hours | Within 5 business days |
| **Medium / Low** (Minor information leakage, UI flaw) | Within 5 business days | Next scheduled release |
