{
    'name': 'Satın Alma',
    'version': '17.0.1.0.0',
    'category': 'Purchase',
    'summary': 'Satın alma siparişleri, tedarikçi yönetimi ve onay süreci',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/satin_alma_views.xml',
        'views/menu.xml',
        'data/demo_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
