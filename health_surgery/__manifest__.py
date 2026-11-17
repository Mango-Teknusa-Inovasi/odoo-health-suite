# -*- coding: utf-8 -*-
{
    'name': 'Operating Room & VK',
    'version': '18.0.1.0.0',
    'category': 'Healthcare/Hospital',
    'summary': 'Surgical Theater, WHO Safety Checklist, PACU Recovery & Delivery Suite VK',
    'description': """
Mangotek Health Suite — Operating Room (OK) & Delivery Suite (VK)
================================================================
Comprehensive surgical operations and labor suite management:
* Multi-disciplinary surgical theater booking (Elective vs Cito)
* WHO Surgical Safety Checklist (Sign In, Time Out, Sign Out)
* Post-Anesthesia Recovery Scoring (Aldrete, Bromage, Steward)
* Intra-operative anesthesia and fluid monitoring record
* Labor & Delivery room (VK) partograph (Kala I-IV) and neonate APGAR
* Automated surgical package tariff split to patient billing
    """,
    'author': 'Mango Teknusa Inovasi',
    'website': 'https://github.com/Mango-Teknusa-Inovasi/odoo-health-suite',
    'license': 'LGPL-3',
    'depends': [
        'health_base',
        'health_emr',
        'health_inpatient',
        'health_billing',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/health_surgery_data.xml',
        'views/health_operating_room_views.xml',
        'views/health_surgical_procedure_views.xml',
        'views/health_surgical_booking_views.xml',
        'views/health_surgical_checklist_views.xml',
        'views/health_anesthesia_record_views.xml',
        'views/health_recovery_score_views.xml',
        'views/health_partus_record_views.xml',
        'views/health_surgery_menus.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 0.0,
    'currency': 'EUR',
}
