# -*- coding: utf-8 -*-
# Copyright (C) 2017 Creu Blanca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InterCompanyStatement(models.TransientModel):
    _name = 'account.statement.inter.company'

    name = fields.Char(required=True)
    reference = fields.Char()

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        domain="[('type', 'in', ['bank', 'cash'])]",
    )

    company_id = fields.Many2one(
        'res.company',
        readonly=True,
        related='journal_id.company_id'
    )

    inter_company_ids = fields.Many2many(
        'res.company',
        related='company_id.inter_company_ids'
    )

    destination_journal_id = fields.Many2one(
        'account.journal',
        string='Destination journal',
        domain="[('type', 'in', ['bank', 'cash']),"
               "('company_id', 'in', inter_company_ids)]",
    )

    destination_company_id = fields.Many2one(
        'res.company',
        readonly=True,
        related='destination_journal_id.company_id'
    )

    company_currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string="Company Currency",
        readonly=True,
        help='Utility field to express amount currency',
        store=True
    )

    amount = fields.Monetary(default=0.0, currency_field='company_currency_id')
    currency_id = fields.Many2one(
        'res.currency'
    )

    def inter_company_statement_values(self, journal):
        return {
            'journal_id': journal.id,
            'name': self.name,
            'reference': self.reference,
        }

    def inter_company_statement_line_values(self, statement, account, amount):
        return {
            'name': self.name,
            'ref': self.reference,
            'account_id': account.id,
            'amount': amount,
            'statement_id': statement.id,
        }

    def create_statement(self, journal, account, amount):
        statement = self.env['account.bank.statement'].create(
            self.inter_company_statement_values(journal)
        )
        statement.onchange_journal_id()
        self.env['account.bank.statement.line'].create(
            self.inter_company_statement_line_values(
                statement, account, amount
            )
        )
        statement.balance_end_real = statement.balance_end
        statement.check_confirm_bank()
        return statement

    @api.multi
    def run(self):
        self.ensure_one()
        inter_company = self.env['account.inter.company'].search([
            ('company_id', '=', self.company_id.id),
            ('related_company_id', '=', self.destination_company_id.id),
        ]).ensure_one()
        statement_1 = self.create_statement(
            self.journal_id, inter_company.account_id, - self.amount
        )
        statement_2 = self.create_statement(
            self.destination_journal_id,
            inter_company.related_account_id,
            self.amount
        )
        result = {
            "type": "ir.actions.act_window",
            "res_model": "account.bank.statement",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["id", "in", [statement_1.id, statement_2.id]]],
        }
        return result
