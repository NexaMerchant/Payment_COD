{
    'name': 'COD Payment Method',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Add Cash on Delivery as a payment method',
    'description': 'This module adds Cash on Delivery (COD) as a payment method in Odoo.',
    'author': 'Steve Liu',
    'website': 'https://github.com/xxl4',
    'depends': ['account','sale','payment'],
    'data': [
        'views/payment_method_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'assets': {
        'web.assets_frontend': [
            'payment_cod/static/src/**/*',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
}