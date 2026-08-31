from datetime import date, timedelta

from odoo.tests.common import TransactionCase


class TestEstateLegacyApi(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.property = cls.env['estate.property'].create({
            'name': 'Legacy API Property',
            'expected_price': 150000,
        })

    def test_property_creation(self):
        self.assertEqual(self.property.state, 'new')
        self.assertEqual(self.property.expected_price, 150000)

    def test_property_defaults(self):
        self.assertEqual(self.property.bedrooms, 2)
        self.assertTrue(self.property.active)
        self.assertEqual(self.property.date_availability, date.today() + timedelta(days=90))

    def test_property_can_be_cancelled(self):
        self.property.action_property_cancel()

        self.assertEqual(self.property.state, 'cancelled')
