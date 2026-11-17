# -*- coding: utf-8 -*-
{
    'name': 'INA-CBG E-Klaim Grouper',
    'version': '18.0.1.0.0',
    'category': 'Healthcare/Billing',
    'summary': 'Kemenkes INA-CBG Case-Mix Grouper, ICD-10/ICD-9 CM & Disparity Audit',
    'description': """
Mangotek Health Suite — INA-CBG E-Klaim Grouper & Disparity Audit
=================================================================
Official Ministry of Health (Kemenkes) INA-CBG E-Klaim hospital integration:
* Diagnostic ICD-10 & surgical ICD-9 CM Case-Mix tariff grouping
* Special CMG top-up calculation (stents, implants, chemotherapy)
* Hospital Real Bill vs INA-CBG reimbursement ceiling disparity audit
* Direct integration with BPJS VClaim 2.0 SEP dossier
* Dual-mode architecture: Internal Mock Simulator + Live Intranet Appliance
    """,
    'author': 'Mango Teknusa Inovasi',
    'website': 'https://github.com/Mango-Teknusa-Inovasi/odoo-health-suite',
    'license': 'LGPL-3',
    'depends': [
        'health_base',
        'health_emr',
        'health_inpatient',
        'health_surgery',
        'health_bpjs_vclaim',
        'health_billing',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/health_inacbg_data.xml',
        'views/health_inacbg_config_views.xml',
        'views/health_inacbg_claim_views.xml',
        'views/health_inacbg_menus.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 0.0,
    'currency': 'EUR',
}
