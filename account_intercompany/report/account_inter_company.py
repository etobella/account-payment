# -*- coding: utf-8 -*-
# Copyright (C) 2017 Creu Blanca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import time

from odoo import api, models, _
from odoo.exceptions import UserError


class CashInvoiceIn(models.AbstractModel):
    _name = 'report.account_intercompany.report_account_inter_company'

    def get_data(self, docs):
        inter_companies = self.env['account.inter.company'].search([
            ('company_id', 'in', docs.company_ids.ids)
        ])
        accounts = self.env['account.account'].browse(
            [inter_company.account_id.id for inter_company in inter_companies]
        )
        res = []
        cr = self.env.cr
        sql = ('''SELECT l.account_id as account_id,\
        COALESCE(SUM(l.debit),0.0) AS debit,\
        COALESCE(SUM(l.credit),0.0) AS credit,\
        COALESCE(SUM(l.credit),0) - COALESCE(SUM(l.debit), 0) as balance\
        FROM account_move_line l\
        WHERE l.account_id in %s\
        GROUP BY l.account_id
        ''')
        params = (tuple(accounts.ids),)
        cr.execute(sql, params)
        for row in cr.dictfetchall():
            account = accounts.filtered(lambda r: r.id == row['account_id'])
            res.append({
                'company': account.company_id.name,
                'name': account.name,
                'code': account.code,
                'debit': row['debit'],
                'credit': row['credit'],
                'balance': row['balance']
            })
        return res

    @api.model
    def get_report_values(self, docids, data=None):
        if not self.env.context.get('active_model'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(
            self.env.context.get('active_ids', []))
        accounts_res = self.get_data(docs)

        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data,
            'docs': docs,
            'time': time,
            'accounts': accounts_res
        }
