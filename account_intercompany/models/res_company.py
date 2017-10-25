# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    account_inter_company_ids = fields.One2many(
        'account.inter.company',
        'company_id'
    )

    inter_company_ids = fields.Many2many(
        'res.company',
        compute='_compute_inter_companies'
    )

    inter_company_journal_id = fields.Many2one(
        'account.journal',
        'Inter company journal',
        domain="[('company_id', '=', id)]"
    )

    @api.depends('account_inter_company_ids')
    def _compute_inter_companies(self):
        for record in self:
            ids = []
            for inter_company in record.account_inter_company_ids:
                if inter_company.related_company_id.inter_company_journal_id:
                    ids.append(inter_company.related_company_id.id)
            record.inter_company_ids = self.env['res.company'].browse(ids)
