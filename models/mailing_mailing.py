# -*- coding: utf-8 -*-
import ast
import logging
from odoo import models

_logger = logging.getLogger(__name__)


class MailingMailing(models.Model):
    _inherit = 'mailing.mailing'

    def action_send_mail(self):
        """Override to mark CRM leads when mailing is sent"""
        result = super().action_send_mail()

        # Mark leads from CRM product mailings
        for mailing in self:
            if mailing.mailing_model_id.model == 'crm.lead':
                # Get leads from domain
                Lead = self.env['crm.lead']
                try:
                    # Parse domain from string
                    # (mailing_domain is stored as string)
                    domain = ast.literal_eval(
                        mailing.mailing_domain
                    ) if mailing.mailing_domain else []
                    leads = Lead.search(domain)

                    if leads:
                        # Mark all leads as email sent
                        leads.mark_email_sent()
                        _logger.info(
                            f'Marked {len(leads)} leads as email_sent '
                            f'after mailing {mailing.id} was sent'
                        )
                except Exception as e:
                    _logger.error(
                        f'Failed to mark leads for mailing {mailing.id}: '
                        f'{str(e)}',
                        exc_info=True
                    )

        return result
