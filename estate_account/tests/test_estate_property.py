from odoo.osv import expression
from odoo.tools import float_compare

from odoo.addons.estate.tests.test_estate_property import TestEstateProperty


class TestEstateAccountProperty(TestEstateProperty):
    def test_action_property_sold(self):
        """Test that everything behaves like it should when selling a property."""

        self._sell_cozy_cottage()

        self.invoice = self.env['account.move'].search(expression.AND([
            [['partner_id', '=', self.cozy_cottage.buyer_id.id]], 
            [('move_type', '=', 'out_invoice')]
            ]))
        self.assertTrue(self.invoice)

        sorted_invoice_lines = self.invoice.invoice_line_ids.sorted(key=lambda r: r.price_unit)
        self.assertEqual(sorted_invoice_lines[0].price_unit, 100)
        self.assertEqual(
            float_compare(
                sorted_invoice_lines[1].price_unit,
                self.cozy_cottage.commission_amount,
                precision_digits=2),
            0)
