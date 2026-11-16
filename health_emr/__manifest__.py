# -*- coding: utf-8 -*-
{
    'name': 'Clinical EMR Core',
    'version': '18.0.1.0.0',
    'category': 'Health/Medical',
    'summary': 'Universal SOAP clinical notes, vital signs tracking, and automated medical certificates',
    'author': 'Mango Teknusa Inovasi',
    'website': 'https://github.com/Mango-Teknusa-Inovasi',
    'license': 'LGPL-3',
    'price': 0.0,
    'currency': 'EUR',
    'depends': ['health_base'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/health_vital_sign_views.xml',
        'views/health_emr_soap_views.xml',
        'views/menu_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
