from odoo import Command, models


class EstateProperty(models.Model):
    _inherit = "estate.property"

    def get_sold_property_invoice_values(self):
        return [{
            'partner_id': record.buyer_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': [
                Command.create({
                    'name': f"{record.commission_rate:g}% commission",
                    'quantity': 1,
                    'price_unit': record.commission_amount,
                }),
                Command.create({
                    'name': "Administrative fees",
                    'quantity': 1,
                    'price_unit': 100,
                }),
            ],
        } for record in self]

    def action_property_sold(self):
        invoice_vals = self.get_sold_property_invoice_values()
        self.env['account.move'].create(invoice_vals)

        return super().action_property_sold()
