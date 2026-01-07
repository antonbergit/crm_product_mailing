# -*- coding: utf-8 -*-
import logging
from datetime import timedelta

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    mailing_triggered_today = fields.Boolean(
        default=False,
        help="Prevents duplicate mailings for the same product on the same day"
    )

    def reset_mailing_trigger(self):
        """Reset mailing trigger flag - called daily by cron"""
        self.search([]).write({'mailing_triggered_today': False})
        _logger.info('Reset mailing triggers for all products')
        return True

    @api.model
    def generate_daily_mailings(self):
        """
        Main cron method - runs daily to generate product
        availability mailings

        Process:
        1. Get configuration
        2. Find products with stock > 0 and not triggered today
        3. For each product:
           a. Determine rule (high/low stock) based on config
           b. Get target leads
           c. Create draft mailing.mailing
           d. Mark product as triggered
        """
        Lead = self.env['crm.lead']
        Mailing = self.env['mailing.mailing']
        Config = self.env['crm.product.mailing.config']

        # Get active configuration
        config = Config.get_config()

        # Get available products not yet processed today
        products = self.search([
            ('qty_available', '>', 0),
            ('mailing_triggered_today', '=', False)
        ])

        _logger.info(
            f'Found {len(products)} products with available stock '
            f'for mailing generation'
        )

        for product in products:
            try:
                # Determine rule based on config threshold
                if product.qty_available >= config.high_stock_threshold:
                    # High stock: target leads with this specific product
                    leads = Lead.search([
                        ('product_id', '=', product.id),
                        ('email_sent', '=', False),
                        ('active', '=', True)
                    ])
                    template = self.env.ref(
                        'crm_product_mailing.mail_template_high_stock',
                        raise_if_not_found=False
                    )
                    rule_name = 'High Stock'
                else:
                    # Low stock: target recent leads with THIS product
                    # Use config days range
                    cutoff_date = (
                        fields.Datetime.now() -
                        timedelta(days=config.low_stock_days_range)
                    )
                    leads = Lead.search([
                        ('product_id', '=', product.id),
                        ('create_date', '>=', cutoff_date),
                        ('email_sent', '=', False),
                        ('active', '=', True),
                    ])
                    template = self.env.ref(
                        'crm_product_mailing.mail_template_low_stock',
                        raise_if_not_found=False
                    )
                    rule_name = 'Low Stock'

                if not leads:
                    _logger.debug(
                        f'No eligible leads for product {product.name}'
                    )
                    continue

                if not template:
                    _logger.warning(
                        f'Email template not found for {rule_name} rule'
                    )
                    continue

                # Create draft mailing
                mailing = Mailing.create({
                    'name': f'Product Available: {product.name}',
                    'subject': template.subject,
                    'body_html': template.body_html,
                    'mailing_model_id': self.env.ref('crm.model_crm_lead').id,
                    'mailing_domain': [('id', 'in', leads.ids)],
                    'state': 'draft',
                    'keep_archives': True,
                })

                # Mark product as processed today
                product.mailing_triggered_today = True

                _logger.info(
                    f'Created mailing {mailing.id} for product '
                    f'{product.name} ({rule_name}, {len(leads)} leads)'
                )

            except Exception as e:
                _logger.error(
                    f'Failed to generate mailing for product '
                    f'{product.name}: {str(e)}',
                    exc_info=True
                )
                # Continue with next product even if one fails
                continue

        return True
