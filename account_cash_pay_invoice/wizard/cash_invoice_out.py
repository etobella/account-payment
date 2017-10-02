# -*- coding: utf-8 -*-
# Copyright (C) 2017 Creu Blanca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, api, models, _
from odoo.exceptions import UserError


class CashInvoiceOut(models.TransientModel):
    _name = 'cash.invoice.out'
    _inherit = 'cash.box.in'

    def _default_company(self):
        active_model = self.env.context.get('active_model', False)
        if active_model:
            active_ids = self.env.context.get('active_ids', False)
            return self.default_company(
                self.env[active_model].browse(active_ids)
            )
        return None

    def _default_currency(self):
        active_model = self.env.context.get('active_model', False)
        if active_model:
            active_ids = self.env.context.get('active_ids', False)
            return self.default_currency(
                self.env[active_model].browse(active_ids)
            )
        return None

    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        required=True
    )
    name = fields.Char(
        related='invoice_id.number'
    )
    company_id = fields.Many2one(
        'res.company',
        default=_default_company,
        required=True,
        readonly=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=_default_currency,
        required=True,
        readonly=True
    )

    def default_company(self, active_resources):
        return active_resources[0].company_id

    def default_currency(self, active_resources):
        return self.default_company(active_resources).currency_id

    @api.onchange('invoice_id')
    def _onchange_invoice(self):
        self.amount = self.invoice_id.residual

    @api.multi
    def _calculate_values_for_statement_line(self, record):
        res = super(CashInvoiceOut, self)._calculate_values_for_statement_line(
            record
        )
        res['invoice_id'] = self.invoice_id.id
        res['account_id'] = self.invoice_id.account_id.id
        res['ref'] = self.invoice_id.number
        res['partner_id'] = self.invoice_id.partner_id.id
        return res
