{
    'name': 'İzin Yönetimi',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Çalışan izin talep ve onay sistemi',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/izin_talep_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'auto_install': False,
}
