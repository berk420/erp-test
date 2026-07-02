{
    'name': 'Satış Yönetimi',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Satış sipariş takibi, müşteri yönetimi ve raporlama',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/satis_views.xml',
        'views/menu.xml',
        'data/demo_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
