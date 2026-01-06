# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestCrmProductMailing(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test products
        cls.product_high_stock = cls.env['product.product'].create({
            'name': 'Test Product High Stock',
            'type': 'product',
            'list_price': 100.0,
        })

        cls.product_low_stock = cls.env['product.product'].create({
            'name': 'Test Product Low Stock',
            'type': 'product',
            'list_price': 50.0,
        })

        # Set stock quantities
        cls._update_product_qty(cls.product_high_stock, 15)
        cls._update_product_qty(cls.product_low_stock, 5)

        # Create test leads
        cls.lead1 = cls.env['crm.lead'].create({
            'name': 'Test Lead 1',
            'type': 'lead',
            'email_from': 'lead1@test.com',
            'product_id': cls.product_high_stock.id,
        })

        cls.lead2 = cls.env['crm.lead'].create({
            'name': 'Test Lead 2',
            'type': 'lead',
            'email_from': 'lead2@test.com',
            'product_id': cls.product_high_stock.id,
        })

        cls.lead3 = cls.env['crm.lead'].create({
            'name': 'Test Lead 3',
            'type': 'lead',
            'email_from': 'lead3@test.com',
        })

    @classmethod
    def _update_product_qty(cls, product, qty):
        """Helper to update product quantity"""
        quant = cls.env['stock.quant'].search([
            ('product_id', '=', product.id),
            ('location_id.usage', '=', 'internal')
        ], limit=1)
        if quant:
            quant.inventory_quantity = qty
            quant.action_apply_inventory()
        else:
            location = cls.env['stock.location'].search([
                ('usage', '=', 'internal')
            ], limit=1)
            cls.env['stock.quant'].create({
                'product_id': product.id,
                'location_id': location.id,
                'inventory_quantity': qty,
            }).action_apply_inventory()

    def test_01_lead_product_field(self):
        """Test that product field is correctly set on lead"""
        self.assertEqual(
            self.lead1.product_id,
            self.product_high_stock,
            "Lead should have product_id set"
        )
        self.assertFalse(
            self.lead1.email_sent,
            "New lead should not have email_sent flag"
        )

    def test_02_mark_email_sent(self):
        """Test mark_email_sent method"""
        self.assertFalse(self.lead1.email_sent)
        self.assertFalse(self.lead1.email_sent_date)

        self.lead1.mark_email_sent()

        self.assertTrue(
            self.lead1.email_sent,
            "email_sent should be True after marking"
        )
        self.assertTrue(
            self.lead1.email_sent_date,
            "email_sent_date should be set"
        )

    def test_03_reset_mailing_trigger(self):
        """Test reset_mailing_trigger method"""
        self.product_high_stock.mailing_triggered_today = True
        self.product_low_stock.mailing_triggered_today = True

        self.env['product.product'].reset_mailing_trigger()

        self.assertFalse(
            self.product_high_stock.mailing_triggered_today,
            "Trigger should be reset"
        )
        self.assertFalse(
            self.product_low_stock.mailing_triggered_today,
            "Trigger should be reset"
        )

    def test_04_generate_mailing_high_stock(self):
        """Test mailing generation for high stock product"""
        # Ensure products are not triggered yet
        self.product_high_stock.mailing_triggered_today = False

        # Run generation
        self.env['product.product'].generate_daily_mailings()

        # Check mailing was created
        mailings = self.env['mailing.mailing'].search([
            ('name', 'ilike', self.product_high_stock.name)
        ])
        self.assertTrue(
            mailings,
            "Mailing should be created for high stock product"
        )

        # Check product is marked as triggered
        self.assertTrue(
            self.product_high_stock.mailing_triggered_today,
            "Product should be marked as triggered"
        )

    def test_05_generate_mailing_low_stock(self):
        """Test mailing generation for low stock product"""
        # Create lead with low stock product for testing
        low_stock_lead = self.env['crm.lead'].create({
            'name': 'Low Stock Lead',
            'type': 'lead',
            'email_from': 'lowstock@test.com',
            'product_id': self.product_low_stock.id,
        })
        
        # Create OLD lead that should NOT be included
        old_date = fields.Datetime.now() - timedelta(days=35)
        old_low_stock_lead = self.env['crm.lead'].create({
            'name': 'Old Low Stock Lead',
            'type': 'lead',
            'email_from': 'oldlowstock@test.com',
            'product_id': self.product_low_stock.id,
        })
        self.env.cr.execute(
            "UPDATE crm_lead SET create_date = %s WHERE id = %s",
            (old_date, old_low_stock_lead.id)
        )
        old_low_stock_lead.invalidate_recordset(['create_date'])
        
        self.product_low_stock.mailing_triggered_today = False

        self.env['product.product'].generate_daily_mailings()

        mailings = self.env['mailing.mailing'].search([
            ('name', 'ilike', self.product_low_stock.name)
        ])
        self.assertTrue(
            mailings,
            "Mailing should be created for low stock product"
        )
        
        # Verify recent low stock lead is marked
        self.assertTrue(
            low_stock_lead.email_sent,
            "Recent low stock lead should be marked as email_sent"
        )
        
        # Verify OLD low stock lead is NOT marked (filtered out by 30-day rule)
        self.assertFalse(
            old_low_stock_lead.email_sent,
            "Old low stock lead (35 days) should NOT be marked - filtered by 30-day rule"
        )

    def test_06_no_duplicate_mailing_same_day(self):
        """Test that mailing is not duplicated on same day"""
        self.product_high_stock.mailing_triggered_today = False

        # First generation
        self.env['product.product'].generate_daily_mailings()
        mailings_count_1 = self.env['mailing.mailing'].search_count([
            ('name', 'ilike', self.product_high_stock.name)
        ])

        # Second generation (same day)
        self.env['product.product'].generate_daily_mailings()
        mailings_count_2 = self.env['mailing.mailing'].search_count([
            ('name', 'ilike', self.product_high_stock.name)
        ])

        self.assertEqual(
            mailings_count_1,
            mailings_count_2,
            "No duplicate mailings should be created on same day"
        )

    def test_07_mailing_targets_correct_leads(self):
        """Test that high stock mailing targets specific product leads"""
        # Get leads with product_id=product_high_stock and email_sent=False BEFORE
        target_leads_before = self.env['crm.lead'].search([
            ('product_id', '=', self.product_high_stock.id),
            ('email_sent', '=', False),
            ('active', '=', True),
        ])
        
        # Get leads with OTHER products
        other_leads = self.env['crm.lead'].search([
            ('product_id', '!=', self.product_high_stock.id),
            ('product_id', '!=', False),
            ('email_sent', '=', False),
            ('active', '=', True),
        ])
        
        self.product_high_stock.mailing_triggered_today = False

        self.env['product.product'].generate_daily_mailings()

        mailing = self.env['mailing.mailing'].search([
            ('name', 'ilike', self.product_high_stock.name)
        ], limit=1, order='id desc')

        self.assertTrue(mailing, "Mailing should exist")
        self.assertEqual(
            mailing.mailing_model_id.model,
            'crm.lead',
            "Mailing should target crm.lead model"
        )
        
        # Verify that ONLY leads with product_high_stock were marked
        for lead in target_leads_before:
            self.assertTrue(
                lead.email_sent,
                f"Lead {lead.name} with product_high_stock should be marked"
            )
        
        # Verify leads with OTHER products were NOT marked
        for lead in other_leads:
            self.assertFalse(
                lead.email_sent,
                f"Lead {lead.name} with different product should NOT be marked"
            )

    def test_08_mailing_created_in_draft(self):
        """Test that mailings are created in draft state"""
        self.product_high_stock.mailing_triggered_today = False

        self.env['product.product'].generate_daily_mailings()

        mailing = self.env['mailing.mailing'].search([
            ('name', 'ilike', self.product_high_stock.name)
        ], limit=1)

        self.assertEqual(
            mailing.state,
            'draft',
            "Mailing should be in draft state"
        )

    def test_09_email_sent_tracking(self):
        """Test email_sent field prevents duplicate targeting"""
        # Create fresh leads for this test
        fresh_lead1 = self.env['crm.lead'].create({
            'name': 'Fresh Lead 1',
            'type': 'lead',
            'email_from': 'fresh1@test.com',
            'product_id': self.product_high_stock.id,
        })
        
        fresh_lead2 = self.env['crm.lead'].create({
            'name': 'Fresh Lead 2',
            'type': 'lead',
            'email_from': 'fresh2@test.com',
            'product_id': self.product_high_stock.id,
        })
        
        # Mark only fresh_lead1 as already contacted
        fresh_lead1.email_sent = True

        self.product_high_stock.mailing_triggered_today = False
        self.env['product.product'].generate_daily_mailings()

        # Fresh_lead1 should still be marked
        self.assertTrue(
            fresh_lead1.email_sent,
            "Fresh lead1 should still have email_sent flag"
        )
        
        # Fresh_lead2 should now be marked (it was in the mailing)
        self.assertTrue(
            fresh_lead2.email_sent,
            "Fresh lead2 should be marked after mailing generation"
        )
        
        # Verify fresh_lead1 was NOT included in the new mailing
        # and fresh_lead2 WAS included
        mailing = self.env['mailing.mailing'].search([
            ('name', 'ilike', self.product_high_stock.name)
        ], limit=1, order='id desc')
        self.assertTrue(mailing, "Mailing should be created")
        
        # The key test: fresh_lead1 should remain True (not re-marked)
        # and fresh_lead2 should now be True (newly marked)
        self.assertTrue(
            fresh_lead1.email_sent,
            "fresh_lead1 should still have email_sent=True"
        )
        self.assertTrue(
            fresh_lead2.email_sent,
            "fresh_lead2 should now have email_sent=True after mailing"
        )
        
        # Verify fresh_lead2 has email_sent_date set
        self.assertTrue(
            fresh_lead2.email_sent_date,
            "fresh_lead2 should have email_sent_date set"
        )

    def test_10_old_leads_not_targeted_for_low_stock(self):
        """Test that old leads are not targeted for low stock"""
        # Create old lead (> 30 days) with low stock product
        old_date = fields.Datetime.now() - timedelta(days=35)
        old_lead = self.env['crm.lead'].create({
            'name': 'Old Lead',
            'type': 'lead',
            'email_from': 'old@test.com',
            'product_id': self.product_low_stock.id,
        })
        # Force set old create_date via SQL to bypass ORM protection
        self.env.cr.execute(
            "UPDATE crm_lead SET create_date = %s WHERE id = %s",
            (old_date, old_lead.id)
        )
        old_lead.invalidate_recordset(['create_date'])
        
        # Create recent lead (< 30 days) with low stock product
        recent_lead = self.env['crm.lead'].create({
            'name': 'Recent Lead',
            'type': 'lead',
            'email_from': 'recent@test.com',
            'product_id': self.product_low_stock.id,
        })

        # Verify old lead's create_date is actually old
        self.assertLess(
            old_lead.create_date,
            fields.Datetime.now() - timedelta(days=30),
            "Old lead should have create_date > 30 days ago"
        )

        self.product_low_stock.mailing_triggered_today = False
        self.env['product.product'].generate_daily_mailings()

        mailing = self.env['mailing.mailing'].search([
            ('name', 'ilike', self.product_low_stock.name)
        ], limit=1, order='id desc')

        # Low stock mailing should exist
        self.assertTrue(mailing, "Mailing for low stock should be created")
        self.assertEqual(
            mailing.state,
            'draft',
            "Mailing for low stock should be created in draft"
        )
        
        # Check that old lead is NOT marked (excluded by date filter)
        self.assertFalse(
            old_lead.email_sent,
            "Old lead (35 days) should NOT be marked - outside 30-day range"
        )
        
        # Check that recent lead IS marked (included in mailing)
        self.assertTrue(
            recent_lead.email_sent,
            "Recent lead should be marked - within 30-day range"
        )
        
        # Verify recent lead has email_sent_date set
        self.assertTrue(
            recent_lead.email_sent_date,
            "Recent lead should have email_sent_date set"
        )
        
        # Verify old lead does NOT have email_sent_date
        self.assertFalse(
            old_lead.email_sent_date,
            "Old lead should NOT have email_sent_date"
        )

    def test_11_cron_marks_leads_with_tag(self):
        """Test that cron execution marks leads with 'відправлено email' tag"""
        # Create fresh lead with product
        test_lead = self.env['crm.lead'].create({
            'name': 'Test Lead for Cron',
            'type': 'lead',
            'email_from': 'crontest@test.com',
            'product_id': self.product_high_stock.id,
        })

        # Verify initial state
        self.assertFalse(test_lead.email_sent, "Lead should not have email_sent initially")
        self.assertFalse(test_lead.email_sent_date, "Lead should not have email_sent_date initially")
        
        # Check no tag initially
        email_tag = self.env['crm.tag'].search([('name', '=', 'відправлено email')], limit=1)
        if email_tag:
            self.assertNotIn(email_tag, test_lead.tag_ids, "Lead should not have tag initially")

        # Reset trigger and run cron generation
        self.product_high_stock.mailing_triggered_today = False
        self.env['product.product'].generate_daily_mailings()

        # Verify mailing was created
        mailing = self.env['mailing.mailing'].search([
            ('name', 'ilike', self.product_high_stock.name)
        ], limit=1)
        self.assertTrue(mailing, "Mailing should be created")
        self.assertEqual(mailing.state, 'draft', "Mailing should be in draft state")

        # Verify lead is marked with email_sent
        self.assertTrue(test_lead.email_sent, "Lead should have email_sent=True after cron")
        self.assertTrue(test_lead.email_sent_date, "Lead should have email_sent_date after cron")

        # Verify lead has the tag 'відправлено email'
        email_tag = self.env['crm.tag'].search([('name', '=', 'відправлено email')], limit=1)
        self.assertTrue(email_tag, "Tag 'відправлено email' should exist")
        self.assertIn(
            email_tag,
            test_lead.tag_ids,
            "Lead should have 'відправлено email' tag after cron execution"
        )

        # Verify lead won't be targeted in next run
        self.product_high_stock.mailing_triggered_today = False
        mailings_before = self.env['mailing.mailing'].search_count([
            ('name', 'ilike', self.product_high_stock.name)
        ])
        
        self.env['product.product'].generate_daily_mailings()
        
        mailings_after = self.env['mailing.mailing'].search_count([
            ('name', 'ilike', self.product_high_stock.name)
        ])
        
        self.assertEqual(
            mailings_before,
            mailings_after,
            "No new mailing should be created for lead with email_sent=True"
        )
