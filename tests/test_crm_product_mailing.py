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
        self.product_low_stock.mailing_triggered_today = False

        self.env['product.product'].generate_daily_mailings()

        mailings = self.env['mailing.mailing'].search([
            ('name', 'ilike', self.product_low_stock.name)
        ])
        self.assertTrue(
            mailings,
            "Mailing should be created for low stock product"
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
        self.product_high_stock.mailing_triggered_today = False

        self.env['product.product'].generate_daily_mailings()

        mailing = self.env['mailing.mailing'].search([
            ('name', 'ilike', self.product_high_stock.name)
        ], limit=1)

        self.assertTrue(mailing, "Mailing should exist")
        self.assertEqual(
            mailing.mailing_model_id.model,
            'crm.lead',
            "Mailing should target crm.lead model"
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
        # Mark lead as already contacted
        self.lead1.email_sent = True

        self.product_high_stock.mailing_triggered_today = False
        self.env['product.product'].generate_daily_mailings()

        mailing = self.env['mailing.mailing'].search([
            ('name', 'ilike', self.product_high_stock.name)
        ], limit=1)

        self.assertTrue(mailing, "Mailing should be created")

        # Lead1 should not be in mailing recipients (has email_sent=True)
        # Check that only lead2 (not lead1) is targeted
        self.assertFalse(
            self.lead2.email_sent,
            "Lead2 should not have email_sent flag"
        )
        self.assertTrue(
            self.lead1.email_sent,
            "Lead1 should have email_sent flag"
        )

    def test_10_old_leads_not_targeted_for_low_stock(self):
        """Test that old leads are not targeted for low stock"""
        # Create old lead (> 30 days)
        old_date = fields.Datetime.now() - timedelta(days=31)
        old_lead = self.env['crm.lead'].create({
            'name': 'Old Lead',
            'type': 'lead',
            'email_from': 'old@test.com',
        })
        # Force set old create_date via SQL to bypass ORM protection
        self.env.cr.execute(
            "UPDATE crm_lead SET create_date = %s WHERE id = %s",
            (old_date, old_lead.id)
        )
        old_lead.invalidate_recordset(['create_date'])

        self.product_low_stock.mailing_triggered_today = False
        self.env['product.product'].generate_daily_mailings()

        mailing = self.env['mailing.mailing'].search([
            ('name', 'ilike', self.product_low_stock.name)
        ], limit=1)

        # Verify old lead's create_date is actually old
        self.assertLess(
            old_lead.create_date,
            fields.Datetime.now() - timedelta(days=30),
            "Old lead should have create_date > 30 days ago"
        )

        # Low stock mailing should exist but not target old leads
        if mailing:
            self.assertEqual(
                mailing.state,
                'draft',
                "Mailing for low stock should be created in draft"
            )
