# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CrmProductMailingConfig(models.Model):
    _name = 'crm.product.mailing.config'
    _description = 'CRM Product Mailing Configuration'
    _rec_name = 'id'

    high_stock_threshold = fields.Integer(
        default=10,
        required=True,
        help="Minimum quantity to trigger high stock rule"
    )

    low_stock_days_range = fields.Integer(
        default=30,
        required=True,
        help="Number of days to look back for leads in low stock rule"
    )

    active = fields.Boolean(
        default=True,
        help="Only one active configuration is used"
    )

    @api.model
    def get_config(self):
        """Get active configuration or create default one"""
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            config = self.create({
                'high_stock_threshold': 10,
                'low_stock_days_range': 30,
            })
        return config

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure only one active config exists"""
        # Check if any of the new records will be active
        has_active = any(vals.get('active', True) for vals in vals_list)
        
        if has_active:
            # Deactivate all existing active configs
            self.search([('active', '=', True)]).write({'active': False})
        
        return super().create(vals_list)

    def write(self, vals):
        """Ensure only one active config exists"""
        if vals.get('active'):
            self.search([('active', '=', True), ('id', '!=', self.id)]).write({
                'active': False
            })
        return super().write(vals)
