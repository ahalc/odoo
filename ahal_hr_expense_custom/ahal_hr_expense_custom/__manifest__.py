# -*- encoding: utf-8 -*-
{
  'name' : 'Customización del módulo hr_expense',
  'summary': 'Coded By: ',
  'author' : 'AHAL',
  'category': 'Custom',
  'website': '',
  'depends' : ['base','hr_expense','account'],
  'data': [            
    'security/ir.model.access.csv',   
    'views/report_expense_sheet.xml',   
    'wizard/import_zip_wizard_view.xml',   
  ],
  'installable': True,
  'auto_install': False,
}
