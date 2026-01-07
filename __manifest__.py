# -*- coding: utf-8 -*-
{
    'name': 'CRM Product Mailing',
    'version': '17.0.1.1.0',
    'category': 'CRM',
    'summary': 'Automated product availability mailings for leads',
    'author': 'KitWorks',
    'website': 'https://kitworks.systems/',
    'depends': [
        'crm',
        'product',
        'stock',
        'mass_mailing',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/config_data.xml',
        'data/mail_template.xml',
        'data/ir_cron.xml',
        'views/crm_lead_views.xml',
        'views/crm_product_mailing_config_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
