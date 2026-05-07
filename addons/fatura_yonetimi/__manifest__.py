{
    'name': 'Fatura Yönetimi',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Basit fatura oluşturma ve takip modülü',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/fatura_views.xml',
        'views/menu.xml',
        'data/demo_musteriler.xml',
        'data/demo_faturalar.xml',
    ],
    'installable': True,
    'auto_install': False,
}
