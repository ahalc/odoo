# -*- coding: utf-8 -*-
{
    'name': 'General Ledger Initial balance',
    'version': '14.0',
    'category': 'Accounting/Accounting',
    'summary': 'This module adds Initial balance to show in General ledger report.',
    'description': """
This module adds Initial balance to show in General ledger report.
Initial balance | General ledger report | ledger report | report.
====================================================================================
    """,
    'author': 'NEDI.',
    'website': 'http://www.nedi.mx',
    'depends': ['account'],
    'data': [
        'data/data.xml',
        'views/account_views.xml',
    ],
    'images': ['static/description/1.jpg'],
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
    'price': 45,
    'currency': 'EUR',
}
