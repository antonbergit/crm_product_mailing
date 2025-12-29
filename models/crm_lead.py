# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    product_id = fields.Many2one(
        comodel_name='product.product',
        tracking=True,
        index=True,
        help="Product that the lead is interested in"
    )

    email_sent = fields.Boolean(
        default=False,
        tracking=True,
        help="Indicates if product availability email has been sent"
    )

    email_sent_date = fields.Datetime(
        readonly=True,
        help="Date when the product availability email was sent"
    )

    def mark_email_sent(self):
        """Mark lead as having received product availability email"""
        self.write({
            'email_sent': True,
            'email_sent_date': fields.Datetime.now()
        })
        return True

    @api.model
    def create(self, vals):
        """Override to handle product_id from website context"""
        # If lead is created from website with product info
        if self._context.get('from_website') and 'website_product_id' in vals:
            vals['product_id'] = vals.pop('website_product_id')
        return super(CrmLead, self).create(vals)
