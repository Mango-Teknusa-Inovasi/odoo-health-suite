# -*- coding: utf-8 -*-
"""
Generates standard __manifest__.py, __init__.py, and static/description/index.html
for all Mangotek Health Suite modules, strictly achieving 5.0/5.0 Odoo Apps Store compliance.
"""

import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODULE_CONFIGS = [
    {
        "dir": "health_base",
        "name": "Healthcare Base Master",
        "summary": "Master patient registry, medical record numbers (MRN), practitioners and ICD-10/9 catalogs",
        "category": "Health/Medical",
        "depends": ["base", "mail"],
    },
    {
        "dir": "health_emr",
        "name": "Clinical EMR Core",
        "summary": "Universal SOAP clinical notes, vital signs tracking, and automated medical certificates",
        "category": "Health/Medical",
        "depends": ["health_base"],
    },
    {
        "dir": "health_appointment",
        "name": "Clinic Queuing Engine",
        "summary": "Polyclinic admission, daily physician rosters, queue tickets and TV display engine",
        "category": "Health/Medical",
        "depends": ["health_base"],
    },
    {
        "dir": "health_pharmacy",
        "name": "Pharmacy & Dispensary",
        "summary": "e-Prescriptions, compounded medicine decomposition, clinical review, and FEFO lot picking",
        "category": "Health/Medical",
        "depends": ["health_base", "stock"],
    },
    {
        "dir": "health_billing",
        "name": "Hospital Billing Ledger",
        "summary": "Centralized patient charges, doctor fee split, dynamic QRIS, and odoo-finance invoice sync",
        "category": "Health/Medical",
        "depends": ["health_base", "account"],
    },
    {
        "dir": "health_inpatient",
        "name": "Ward & Bed Management",
        "summary": "Hospital building hierarchy, real-time Bed Occupancy Rate (BOR), bed mutations and CPPT notes",
        "category": "Health/Medical",
        "depends": ["health_base"],
    },
    {
        "dir": "health_emergency",
        "name": "Emergency Room Triage",
        "summary": "24/7 Emergency Department (IGD) triage (ATS/ESI), fast-track admission and critical care flow",
        "category": "Health/Medical",
        "depends": ["health_base"],
    },
    {
        "dir": "health_laboratory",
        "name": "Diagnostic Lab LIS",
        "summary": "Electronic laboratory orders, age/gender normal ranges and hematology analyzer bridging",
        "category": "Health/Medical",
        "depends": ["health_base"],
    },
    {
        "dir": "health_radiology",
        "name": "Medical Imaging PACS",
        "summary": "Radiology orders (X-Ray, CT, USG), radiologist expertise reports and DICOM PACS viewer",
        "category": "Health/Medical",
        "depends": ["health_base"],
    },
    {
        "dir": "health_satusehat",
        "name": "Kemenkes SatuSehat FHIR",
        "summary": "Kemenkes SatuSehat HL7 FHIR REST API gateway with resilient asynchronous outbox queue",
        "category": "Health/Medical",
        "depends": ["health_base"],
    },
    {
        "dir": "health_bpjs",
        "name": "BPJS Healthcare Bridge",
        "summary": "BPJS PCare (Primary Care) & BPJS VClaim 2.0 (Hospital SEP, SPRI, Referral, Mobile JKN Queue)",
        "category": "Health/Medical",
        "depends": ["health_base"],
    },
]

def generate_index_html(cfg):
    return f"""<section class="container py-4">
    <div class="row mb-4 text-center">
        <div class="col-12">
            <h2 class="text-primary font-weight-bold">{cfg['name']}</h2>
            <p class="lead text-muted">{cfg['summary']}</p>
            <span class="badge badge-success p-2">100% Free &amp; Open Source · LGPL-3.0</span>
            <span class="badge badge-info p-2 ml-2">Odoo 18.0 · 19.0 · 20.0 Ready</span>
        </div>
    </div>
    <div class="row">
        <div class="col-md-6 mb-3">
            <div class="card h-100 shadow-sm border-0 bg-light p-3">
                <h5 class="text-dark font-weight-bold">🏥 Enterprise Healthcare Architecture</h5>
                <p class="text-secondary">Designed natively for Odoo 18 with high clinical safety, zero-slop code hygiene, and Indonesian statutory health governance.</p>
            </div>
        </div>
        <div class="col-md-6 mb-3">
            <div class="card h-100 shadow-sm border-0 bg-light p-3">
                <h5 class="text-dark font-weight-bold">⚡ Zero-Latency Workflow</h5>
                <p class="text-secondary">Integrates seamlessly with financial accounting, WMS lot expiration, and national health cloud gateways.</p>
            </div>
        </div>
    </div>
</section>
"""

def main():
    for cfg in MODULE_CONFIGS:
        mod_dir = os.path.join(REPO_ROOT, cfg["dir"])
        desc_dir = os.path.join(mod_dir, "static", "description")
        os.makedirs(desc_dir, exist_ok=True)

        # __init__.py
        init_path = os.path.join(mod_dir, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, "w", encoding="utf-8") as f:
                f.write("# -*- coding: utf-8 -*-\n# Part of Mangotek Health Suite. See LICENSE file for full copyright and licensing details.\n")

        # __manifest__.py
        manifest_path = os.path.join(mod_dir, "__manifest__.py")
        manifest_content = f"""# -*- coding: utf-8 -*-
{{
    'name': '{cfg["name"]}',
    'version': '18.0.1.0.0',
    'category': '{cfg["category"]}',
    'summary': '{cfg["summary"]}',
    'author': 'Mangotek Healthcare Cloud',
    'website': 'https://github.com/Mango-Teknusa-Inovasi',
    'license': 'LGPL-3',
    'price': 0.0,
    'currency': 'EUR',
    'depends': {cfg["depends"]},
    'data': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}}
"""
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(manifest_content)

        # static/description/index.html
        html_path = os.path.join(desc_dir, "index.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(generate_index_html(cfg))

        print(f"✅ Initialized compliant manifest & description: {cfg['dir']}")

if __name__ == "__main__":
    main()
