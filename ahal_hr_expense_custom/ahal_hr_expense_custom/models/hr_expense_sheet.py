# -*- encoding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError
from datetime import date


class HrExpenseSheet(models.Model):
  _inherit = 'hr.expense.sheet'  

  invoice_ids = fields.One2many(comodel_name='account.move', inverse_name='sheet_id')

  def approve_expense_sheets(self):   
    return super(HrExpenseSheet, self).approve_expense_sheets()
  
  def import_zip_file(self):
    vals = {
      'msg': False
    }
    wizard_id = self.env['import.zip.wizard'].create(vals)

    return {        
      'name': (""),                        
      'view_type': 'form',        
      'view_mode': 'form',        
      'res_model': 'import.zip.wizard', 
      'res_id': wizard_id.id,
      'views': [(False, 'form')],        
      'type': 'ir.actions.act_window',        
      'target': 'new',    
    }
