# -*- coding: utf-8 -*-
# Copyright (C) 2017 Creu Blanca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InterCompanyReport(models.TransientModel):
    _name = 'account.inter.company.report'

    company_ids = fields.Many2many(
        'res.company',
        default=lambda self: self.env.user.company_id
    )

    def _print_report(self, data):
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env.ref(
            'account_intercompany.action_report_account_inter_company'
        ).with_context(landscape=True).report_action(records, data=data)

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        return self._print_report(data)
