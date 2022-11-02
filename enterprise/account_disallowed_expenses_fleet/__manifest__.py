# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.
{
    'name': 'Disallowed Expenses on Fleets',
    'category': 'Accounting/Accounting',
    'summary': 'Manage disallowed expenses with fleets',
    'description': "",
    'version': '1.0',
    'depends': ['account_fleet', 'account_disallowed_expenses'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_disallowed_expenses_category_views.xml',
        'views/account_move_views.xml',
        'views/fleet_vehicle_views.xml',
        'views/report_financial.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
    'license': 'TEEL-1',
}
