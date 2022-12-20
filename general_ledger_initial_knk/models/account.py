# -*- coding: utf-8 -*-
import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tools import date_utils


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    initial_balance = fields.Monetary(default=0.0, currency_field='company_currency_id', group_operator="avg")
    # initial_balance = fields.Monetary(compute="_compute_initial_balance2", default=0.0, currency_field='company_currency_id')

    # def _compute_initial_balance2(self):
    #     for record in self.search([]):
    #         if record.id == 26:
    #             line = self.env['account.move.line'].search([
    #                 ('account_id', '=', record.account_id.id),
    #                 # ('partner_id', '=', record.partner_id.id),
    #                 ('id', '<', record.id)
    #             ], order="id desc", limit=1)
    #             print (line)
    #             record.initial_balance = line.balance
    #         else:
    #             record.initial_balance = 0.0

    def _compute_initial_balance(self):
        for record in self.search([]):
            line = self.env['account.move.line'].search([
                ('account_id', '=', record.account_id.id),
                ('move_id.state', '=', 'posted'),
                # ('partner_id', '=', record.partner_id.id),
                ('id', '<', record.id)
            ], order="id desc", limit=1)
            record.initial_balance = line.balance

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """
            Override read_group to calculate the sum of the non-stored fields that depend on the user context
        """
        res = super(AccountMoveLine, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        print ("LLLLLLLL", groupby)
        if 'date:week' in groupby:
            for record in self.search([]):
                start_date = record.date + datetime.timedelta(-record.date.weekday(), weeks=-1)
                end_date = record.date + datetime.timedelta(-record.date.weekday() - 1)
                line = self.env['account.move.line'].search([
                    ('account_id', '=', record.account_id.id),
                    ('move_id.state', '=', 'posted'),
                    ('date', '>=', start_date),
                    ('date', '<=', end_date),
                    # ('id', '<', record.id),
                ])
                record.initial_balance = sum(line.mapped('balance')) if line else 0.0
        elif 'date:month' in groupby:
            for record in self.search([]):
                start_date = (record.date - relativedelta(months=1)).replace(day=1)
                end_date = record.date.replace(day=1) - datetime.timedelta(days=1)
                line = self.env['account.move.line'].search([
                    ('account_id', '=', record.account_id.id),
                    ('move_id.state', '=', 'posted'),
                    ('date', '>=', start_date),
                    ('date', '<=', end_date),
                    # ('id', '<', record.id),
                ])
                record.initial_balance = sum(line.mapped('balance')) if line else 0.0
        elif 'date:year' in groupby:
            for record in self.search([]):
                start_date = record.date.replace(day=1, month=1) - relativedelta(years=1)
                end_date = record.date.replace(day=31, month=12) - relativedelta(years=1)
                line = self.env['account.move.line'].search([
                    ('account_id', '=', record.account_id.id),
                    ('move_id.state', '=', 'posted'),
                    ('date', '>=', start_date),
                    ('date', '<=', end_date),
                    # ('id', '<', record.id),
                ])
                record.initial_balance = sum(line.mapped('balance')) if line else 0.0
        elif 'date:day' in groupby:
            for record in self.search([]):
                start_date = record.date - datetime.timedelta(days=1)
                line = self.env['account.move.line'].search([
                    ('account_id', '=', record.account_id.id),
                    ('move_id.state', '=', 'posted'),
                    ('date', '>=', start_date),
                    ('date', '<', record.date),
                    # ('id', '<', record.id),
                ])
                record.initial_balance = sum(line.mapped('balance')) if line else 0.0
        elif 'date:quarter' in groupby:
            for record in self.search([]):
                quarter_start, quarter_end = date_utils.get_quarter(record.date)
                date = quarter_start - datetime.timedelta(days=1)
                start_date, end_date = date_utils.get_quarter(date)
                line = self.env['account.move.line'].search([
                    ('account_id', '=', record.account_id.id),
                    ('move_id.state', '=', 'posted'),
                    ('date', '>=', start_date),
                    ('date', '<=', end_date),
                    # ('id', '<', record.id),
                ])
                record.initial_balance = sum(line.mapped('balance')) if line else 0.0
        else:
            for record in self.search([]):
                line = self.env['account.move.line'].search([
                    ('account_id', '=', record.account_id.id),
                    ('move_id.state', '=', 'posted'),
                    # ('partner_id', '=', record.partner_id.id),
                    ('id', '<', record.id)
                ], order="id desc", limit=1)
                record.initial_balance = line.balance
        return res
