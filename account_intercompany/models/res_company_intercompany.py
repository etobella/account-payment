# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountInterCompany(models.Model):
    _name = 'account.inter.company'

    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True
    )

    inverse_inter_company_id = fields.Many2one(
        'account.inter.company',
        ondelete='cascade'
    )

    related_company_id = fields.Many2one(
        'res.company',
        'Related company',
        domain="[('id', '!=', company_id)]",
        required=True,
        related='inverse_inter_company_id.company_id'
    )

    account_id = fields.Many2one(
        'account.account',
        'Account',
        required=True,
        domain="[('company_id', '=', company_id)]"
    )

    related_account_id = fields.Many2one(
        'account.account',
        'Related account',
        related='inverse_inter_company_id.account_id',
        required=True,
        domain="[('company_id', '=', related_company_id)]",
    )

    @api.constrains('company_id', 'related_company_id')
    def _check_company(self):
        if self.env['account.inter.company'].search_count([
            ('company_id', '=', self.company_id.id),
            ('related_company_id', '=', self.related_company_id.id)
        ]) > 1:
            raise ValidationError(_(
                'Only one inter company record is allowed between two '
                'companies'
            ))

    @api.onchange('related_company_id')
    def _onchange_related_company_id(self):
        self.related_account_id = False

    @api.onchange('company_id')
    def _onchange_company_id(self):
        self.account_id = False

    def create(self, vals):
        res = super(AccountInterCompany, self).create(vals)
        inverse = super(AccountInterCompany, self).create({
            'company_id': vals['related_company_id'],
            'account_id': vals['related_account_id'],
            'inverse_inter_company_id': res.id,
        })
        res.write({'inverse_inter_company_id': inverse.id})
        return res
