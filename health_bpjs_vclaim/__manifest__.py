# -*- coding: utf-8 -*-
{
    'name': 'BPJS Hospital VClaim',
    'version': '18.0.1.0.0',
    'category': 'Healthcare/Bridging',
    'summary': 'BPJS Health VClaim 2.0 Bridging, SEP Generator, SPRI & Surat Kontrol',
    'description': """
Mangotek Health Suite — BPJS Hospital Claims & VClaim 2.0
=========================================================
Official BPJS Kesehatan FKRTL hospital bridging integration:
* Automated Inpatient & Outpatient SEP (Surat Eligibilitas Peserta) generation
* SPRI (Surat Perintah Rawat Inap) bridging for elective hospital admissions
* Surat Rencana Kontrol Poliklinik management and validation
* Official Cetak SEP continuous document PDF layout
* Dual-mode architecture: Internal Mock Simulator + Live VClaim Web Service
    """,
    'author': 'Mango Teknusa Inovasi',
    'website': 'https://github.com/Mango-Teknusa-Inovasi/odoo-health-suite',
    'license': 'LGPL-3',
    'depends': [
        'health_base',
        'health_bpjs',
        'health_appointment',
        'health_inpatient',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/health_bpjs_vclaim_data.xml',
        'report/health_sep_report.xml',
        'views/health_bpjs_vclaim_config_views.xml',
        'views/health_bpjs_spri_views.xml',
        'views/health_bpjs_surat_kontrol_views.xml',
        'views/health_bpjs_sep_views.xml',
        'views/health_bpjs_vclaim_menus.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 0.0,
    'currency': 'EUR',
}
