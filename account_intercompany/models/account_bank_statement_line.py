# -*- coding: utf-8 -*-
# Copyright (C) 2017 Creu Blanca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class BankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    def _prepare_reconciliation_move(self, move_ref):
        res = super(BankStatementLine, self)._prepare_reconciliation_move(
            move_ref
        )
        inter_company_id = self.env.context.get('inter_company_id', False)
        if inter_company_id:
            related_company_id = inter_company_id.related_company_id
            res['journal_id'] = related_company_id.inter_company_journal_id.id
        return res

    def _prepare_reconciliation_move_line(self, move, amount):
        res = super(BankStatementLine, self)._prepare_reconciliation_move_line(
            move, amount
        )
        inter_company_id = self.env.context.get('inter_company_id', False)
        if inter_company_id:
            res['account_id'] = inter_company_id.related_account_id.id
        return res

    def _prepare_inter_company_move_line(self, move, account, debit, credit):
        company_currency = self.journal_id.company_id.currency_id
        statement_currency = self.journal_id.currency_id or company_currency
        st_line_currency = self.currency_id or statement_currency
        st_line_currency_rate = self.currency_id and (
            self.amount_currency / self.amount
        ) or False
        ctx = dict(self._context, date=self.date)
        aml_dict = {
            'move_id': move.id,
            'account_id': account.id,
            'partner_id': self.partner_id.id,
            'statement_line_id': self.id,
            'debit': debit,
            'credit': credit
        }
        if st_line_currency.id != company_currency.id:
            aml_dict['amount_currency'] = aml_dict['debit'] - aml_dict[
                'credit']
            aml_dict['currency_id'] = st_line_currency.id
            if (
                self.currency_id and
                statement_currency.id == company_currency.id and
                st_line_currency_rate
            ):
                # Statement is in company currency but the transaction is in
                # foreign currency
                aml_dict['debit'] = company_currency.round(
                    aml_dict['debit'] / st_line_currency_rate)
                aml_dict['credit'] = company_currency.round(
                    aml_dict['credit'] / st_line_currency_rate)
            elif self.currency_id and st_line_currency_rate:
                # Statement is in foreign currency and the transaction is in
                # another one
                aml_dict['debit'] = statement_currency.with_context(
                    ctx
                ).compute(
                    aml_dict['debit'] / st_line_currency_rate,
                    company_currency
                )
                aml_dict['credit'] = statement_currency.with_context(
                    ctx
                ).compute(
                    aml_dict['credit'] / st_line_currency_rate,
                    company_currency
                )
            else:
                # Statement is in foreign currency and no extra currency is
                # given for the transaction
                aml_dict['debit'] = st_line_currency.with_context(ctx).compute(
                    aml_dict['debit'], company_currency)
                aml_dict['credit'] = st_line_currency.with_context(
                    ctx).compute(aml_dict['credit'], company_currency)
        elif statement_currency.id != company_currency.id:
            # Statement is in foreign currency but the transaction is in
            # company currency
            prorata_factor = (
                aml_dict['debit'] - aml_dict['credit']
            ) / self.amount_currency
            aml_dict['amount_currency'] = prorata_factor * self.amount
            aml_dict['currency_id'] = statement_currency.id
        return aml_dict

    @api.multi
    def fast_counterpart_creation(self):
        aml_obj = self.env['account.move.line']
        for st_line in self:
            invoice = st_line.invoice_id
            if (
                invoice and
                invoice.company_id.id != st_line.statement_id.company_id.id
            ):
                move_line = invoice.move_id.line_ids.filtered(
                    lambda r: r.account_id.id == invoice.account_id.id
                )
                inter_company = self.env['account.inter.company'].search([
                    ('company_id', '=', st_line.statement_id.company_id.id),
                    ('related_company_id', '=', invoice.company_id.id)
                ])
                debit = st_line.amount < 0 and -st_line.amount or 0.0
                credit = st_line.amount > 0 and st_line.amount or 0.0
                statement = st_line.statement_id
                account = statement.journal_id.default_debit_account_id
                if st_line.amount >= 0:
                    account = statement.journal_id.default_credit_account_id
                vals = {
                    'name': st_line.name,
                    'debit': debit,
                    'credit': credit,
                    'move_line': move_line
                }
                st_line.with_context({
                    'inter_company_id': inter_company
                }).process_reconciliation(counterpart_aml_dicts=[vals])
                move = self.env['account.move'].create(
                    st_line._prepare_reconciliation_move(
                        st_line.statement_id.name
                    )
                )
                aml_obj.with_context(check_move_validity=False).create(
                    st_line._prepare_inter_company_move_line(
                        move,
                        inter_company.account_id,
                        debit,
                        credit
                    )
                )
                aml_obj.with_context(check_move_validity=False).create(
                    st_line._prepare_inter_company_move_line(
                        move,
                        account,
                        credit,
                        debit
                    )
                )
                st_line_amount = -sum([x.balance for x in move.line_ids])
                import logging
                logging.info(st_line_amount)
                move.post()

            else:
                super(BankStatementLine, st_line).fast_counterpart_creation()
