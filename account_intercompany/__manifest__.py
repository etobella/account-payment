# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Inter company accounting',
    'version': '1',
    'summary': 'Management of inter company accounting',
    'sequence': 30,
    'category': 'Creu Blanca',
    'website': 'http://www.creublanca.es',
    'depends': ['account', 'account_cash_invoice'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/res_company_views.xml',
        'wizard/cash_invoice_in.xml',
        'wizard/cash_invoice_out.xml',
    ],
    'demo': [

    ],
    "installable": True,
    'application': True,
    'auto_install': False,
}
