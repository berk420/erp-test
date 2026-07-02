{
    'name': 'Muhasebe Yönetimi',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Gelir-gider takibi, bütçe yönetimi ve finansal raporlama',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/muhasebe_views.xml',
        'views/menu.xml',
        'data/demo_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
