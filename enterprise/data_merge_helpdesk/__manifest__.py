# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

{
    'name': 'Helpdesk Merge action',
    'version': '1.0',
    'category': 'Productivity/Data Cleaning',
    'summary': 'Add Merge action in contextual menu of helpdesk ticket model.',
    'description': """Add Merge action in contextual menu of helpdesk ticket model.""",
    'website': '',
    'depends': ['data_merge', 'helpdesk'],
    'data': [
        'data/ir_model_data.xml',
    ],
    'auto_install': True,
    'license': 'TEEL-1',
}
