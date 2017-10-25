# -*- coding: utf-8 -*-
# Copyright (C) 2017 Creu Blanca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class CashInvoiceOut(models.TransientModel):
    _inherit = 'cash.invoice.out'

    inter_company_ids = fields.Many2many(
        'res.company',
        related='company_id.inter_company_ids'
    )
