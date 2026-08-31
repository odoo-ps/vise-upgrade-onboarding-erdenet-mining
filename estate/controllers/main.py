from odoo import http
from odoo.http import request


class EstateController(http.Controller):
    @http.route(
        '/estate/properties',
        type='json',
        auth='user',
        methods=['POST'],
        csrf=False,
    )
    def properties(self, postcode=None, limit=20):
        domain = [('postcode', '=', postcode)] if postcode else []
        properties = request.env['estate.property'].search(domain, limit=int(limit))
        return properties.read([
            'name',
            'postcode',
            'expected_price',
            'selling_price',
            'state',
        ])

    @http.route(
        '/estate/offers/create',
        type='json',
        auth='user',
        methods=['POST'],
        csrf=False,
    )
    def create_offer(self, property_id, partner_id, price, validity=7):
        offer = request.env['estate.property.offer'].create({
            'property_id': int(property_id),
            'partner_id': int(partner_id),
            'price': float(price),
            'validity': int(validity),
        })
        return {
            'id': offer.id,
            'property_id': offer.property_id.id,
            'price': offer.price,
            'date_deadline': offer.date_deadline.isoformat(),
        }
