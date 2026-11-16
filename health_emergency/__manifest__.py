# -*- coding: utf-8 -*-
{
    'name': 'Emergency Room Triage',
    'version': '18.0.1.0.0',
    'category': 'Health/Medical',
    'summary': 'Australasian/ESI triage categories, ABCD protocols, Mr. X fast-track and emergency transfers',
    'author': 'Mangotek Healthcare Cloud',
    'website': 'https://github.com/Mango-Teknusa-Inovasi',
    'license': 'LGPL-3',
    'price': 0.0,
    'currency': 'EUR',
    'depends': ['health_base', 'health_emr', 'health_inpatient'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/health_emergency_triage_views.xml',
        'views/menu_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
