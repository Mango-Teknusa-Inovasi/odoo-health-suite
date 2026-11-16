# -*- coding: utf-8 -*-
{
    'name': 'Kemenkes SatuSehat FHIR',
    'version': '18.0.1.0.0',
    'category': 'Health/Medical',
    'summary': 'Kemenkes SatuSehat HL7 FHIR REST API gateway with resilient asynchronous outbox queue',
    'author': 'Mango Teknusa Inovasi',
    'website': 'https://github.com/Mango-Teknusa-Inovasi',
    'license': 'LGPL-3',
    'price': 0.0,
    'currency': 'EUR',
    'depends': ['health_base'],
    'data': [
        'security/ir.model.access.csv',
        'views/satusehat_config_views.xml',
        'views/health_integration_log_views.xml',
        'views/menu_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
