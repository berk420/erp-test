{
    'name': 'Stok Yönetimi',
    'version': '17.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Ürün stok takibi, depo yönetimi ve stok hareketleri',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/stok_views.xml',
        'views/menu.xml',
        'data/demo_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
