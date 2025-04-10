{
    'name': 'COD Payment Method',
    'version': '16.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Add Cash on Delivery as a payment method',
    'description': 'This module adds Cash on Delivery (COD) as a payment method in Odoo.',
    'author': 'Steve Liu',
    'website': 'https://github.com/xxl4',
    'depends': ['account','sale','payment'],
    'data': [
       'data/payment_provider_data.xml',  # Depends on views/payment_method_views.xml
       'views/payment_method_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}