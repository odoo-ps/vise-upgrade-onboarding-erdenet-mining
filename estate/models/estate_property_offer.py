from datetime import date, timedelta

from odoo import _, api, exceptions, fields, models
from odoo.fields import Datetime
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class PropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = "Purchase offer for a real estate property"
    _order = 'price DESC'

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)
    price = fields.Monetary(currency_field='currency_id')
    status = fields.Selection(string="Offer Status",copy=False, selection=[('accepted', "Accepted"), ('refused', "Refused")])
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_date_deadline')
    is_expired = fields.Boolean(compute='_compute_is_expired')
    property_type_id = fields.Many2one(related='property_id.property_type_id', store=True)

    _sql_constraints = [
        ('_check_price', 'CHECK(price > 0)', "The price must be strictly positive"),
    ]

    @api.depends('validity')
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = (record.create_date or Datetime.today()) + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            record.validity = (record.date_deadline - record.create_date.date()).days

    @api.depends('date_deadline', 'status')
    def _compute_is_expired(self):
        for record in self:
            record.is_expired = bool(
                record.date_deadline
                and record.date_deadline < date.today()
                and not record.status
            )

    @api.constrains('price')
    def _check_selling_price_90_percent(self):
        for record in self:
            if float_compare(record.price, 0.9 * record.property_id.expected_price, precision_digits=2) == -1:
                raise exceptions.UserError(_("The selling price cannot be lower than 90% of the expected price"))

    @api.model
    def create(self, vals):
        property = self.env['estate.property'].browse(vals['property_id'])
        if property.state == 'sold':
            raise UserError(_("Cannot create an offer for a sold property"))
        property.state = 'offer_received'
        return super().create(vals)

    @api.depends('property_id', 'property_id.offer_ids')
    def action_offer_accept(self):
        for record in self:
            if any(o.status == 'accepted' for o in record.property_id.offer_ids):
                raise exceptions.UserError(_("Cannot accept more than one offer"))
            if float_compare(record.price, 0.9 * record.property_id.expected_price, precision_digits=2) == -1:
                raise exceptions.UserError(_("The selling price cannot be lower than 90% of the expected price"))
            record.status = 'accepted'
            record.property_id.buyer_id = record.partner_id
            record.property_id.state = 'offer_accepted'
            record.property_id.selling_price = record.price

    def action_offer_refuse(self):
        self.status = 'refused'  # assigns the same value to all the records
