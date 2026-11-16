# Odoo Apps Store Publishing & Vendor Guidelines (PUBLISHING.md)

> **Mandatory Standards for Publishing Modules to the Official Odoo Apps Store (`apps.odoo.com`)**  
> **Target Rating:** 5.0 / 5.0 Vendor Quality Score  
> **Target Editions:** Odoo 18.0, 19.0, 20.0 (Community & Enterprise)

---

## 1. Overview & 5.0 Quality Rating Criteria

The official Odoo Apps Store evaluates submissions against strict automated and manual quality criteria. Every module in **Mangotek Health Suite** must pass all criteria to earn a top-tier **5.0 / 5.0** rating upon publication:

| Criterion | Description | Requirement for 5.0 Score |
|:---|:---|:---|
| **Criterion 1: Icon** | Module launcher icon | `static/description/icon.png` (PNG format, $50\times50$ or $100\times100\text{px}$, crisp vector geometry). |
| **Criterion 2: Cover Image** | Store banner image | `images: ['static/description/banner.png']` declared in manifest, resolution $1200\times630\text{px}$. |
| **Criterion 3: Summary** | Functional headline | Manifest `summary` key: concise, max 100 characters, no marketing buzzwords. |
| **Criterion 4: Category** | Store catalog taxonomy | Must map to an official Odoo Apps category (`Medical`, `Health`, `Inventory`, `Point of Sale`). |
| **Criterion 5: Documentation** | Presentation page | `static/description/index.html`: semantic HTML5, zero `<script>` tags, zero unapproved external links. |

---

## 2. Manifest (`__manifest__.py`) Specifications

Every module's `__manifest__.py` file must be a valid Python dictionary complying with these explicit rules:

```python
{
    'name': 'Clinical EMR Core',           # Rule 1: <= 25 characters, explicit, no adjectives
    'version': '18.0.1.0.0',              # Rule 2: <odoo_version>.major.minor.patch
    'category': 'Health/Medical',          # Rule 3: Official Odoo category
    'summary': 'Universal SOAP clinical notes and vital signs charting for clinicians',
    'author': 'Mangotek Healthcare Cloud',
    'website': 'https://github.com/Mango-Teknusa-Inovasi',
    'license': 'LGPL-3',                  # Rule 4: Explicit LGPL-3 declaration
    'price': 0.0,                         # Rule 5: Free tier pricing
    'currency': 'EUR',                    # Rule 5: Official store currency
    'depends': ['health_base', 'mail'],   # Rule 6: Non-empty dependency list
    'data': [
        'security/health_emr_security.xml',
        'security/ir.model.access.csv',
        'views/health_emr_soap_views.xml',
        'views/health_vital_sign_views.xml',
        'views/menu_views.xml',
    ],
    'images': ['static/description/banner.png'],  # Rule 7: Banner cover image
    'installable': True,
    'application': True,                  # Set to True for top-level apps, False for technical add-ons
    'auto_install': False,
}
```

### Detailed Validation Rules:
1. **Module Name (`name`)**:
   - Must not exceed **25 characters**.
   - Must be descriptive and functional (e.g. `Clinical EMR Core`, `Ward Bed Management`).
   - **FORBIDDEN WORDS:** Do not use promotional adjectives (`Best`, `Awesome`, `Pro`, `Free`, `Ultimate`) or vendor prefixes (`Mangotek ...`) in the public display name.
2. **Version Format (`version`)**:
   - Must follow `<odoo_version>.<major>.<minor>.<patch>` (e.g. `18.0.1.0.0`).
3. **License (`license`)**:
   - Must be explicitly set to `'LGPL-3'`.
4. **Price & Currency**:
   - For open-source free tiers: `'price': 0.0` and `'currency': 'EUR'`.
5. **Assets Presence**:
   - `static/description/icon.png` **MUST** exist on disk.
   - `static/description/banner.png` **MUST** exist on disk.
   - `static/description/index.html` **MUST** exist on disk.

---

## 3. HTML Description Guidelines (`static/description/index.html`)

The Odoo Apps Store parser rejects submissions containing unapproved markup:

1. **Forbidden Elements**:
   - `<script>` tags are strictly forbidden and will cause instant rejection.
   - Inline styles should be kept clean; use Bootstrap classes natively supported by Odoo (`container`, `row`, `col-12`, `card`, `badge`).
2. **External Link Restrictions**:
   - Only YouTube video embeds (`youtube.com/embed/...`) and verified support URLs are permitted.
   - Any broken or unauthorized third-party tracking links will trigger validation failure.
3. **Responsive Structure**:
   - Wrap content in `<div class="container">`.
   - Feature sections must include clear benefit highlights, screenshots, and configuration walkthroughs.

---

## 4. Automated Compliance Verification Script

To ensure zero submission errors, run the automated compliance auditor before pushing any module updates:

```bash
# Run store validation across all modules
python scripts/validate_apps_store.py
```

### What the Validator Audits:
- Validates AST syntax of every `__manifest__.py`.
- Checks character limits on `name` ($\le 25\text{ chars}$) and bans restricted words.
- Confirms version string matches `^\d+\.\d+\.\d+\.\d+\.\d+$`.
- Verifies existence and byte sizes of `icon.png` and `banner.png`.
- Inspects `static/description/index.html` for forbidden `<script>` tags or external URL violations.

---

## 5. Release & Tagging Lifecycle

1. **Branching**:
   - Development branches: `18.0-dev-<feature-name>`
   - Production stable branch: `18.0`
2. **Release Tags**:
   - When preparing a release for the Odoo Apps Store, create an annotated Git tag:
     ```bash
     git tag -a v18.0.1.0.0 -m "Release v18.0.1.0.0: Mangotek Health Suite Core"
     git push origin v18.0.1.0.0
     ```
3. **Changelog**:
   - Document all user-facing changes, fixes, and schema migrations in `CHANGELOG.md`.
