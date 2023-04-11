# -*- encoding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError
from datetime import date


class AccountMove(models.Model):
  _inherit = 'account.move'  

  sheet_id = fields.Many2one(comodel_name='hr.expense.sheet', string='Facturas de proveedor')
  uuid_xml = fields.Char(string="UUID")

