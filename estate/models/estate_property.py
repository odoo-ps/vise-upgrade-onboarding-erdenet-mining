from datetime import date, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Property(models.Model):
    _name = 'estate.property'
    _description = "Estate Property"
    _order = 'id DESC'

    name = fields.Char(required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)
    expected_price = fields.Monetary(required=True)
    commission_rate = fields.Float(
        string="Commission Rate (%)",
        default=6.0,
    )
    commission_amount = fields.Monetary(
        compute='_compute_commission_amount',
    )
    property_type_id = fields.Many2one('estate.property.type', string="Property Type")
    channel_id = fields.Many2one('discuss.channel', string="Discussion Channel")
    state = fields.Selection(
        selection=[('new', "New"), ('offer_received', "Offer Received"), ('offer_accepted', "Offer accepted"), ('sold', "Sold"), ('cancelled', "Cancelled")],
        default='new',
    )
    description = fields.Html()
    postcode = fields.Char()
    selling_price = fields.Monetary(copy=False, readonly=True)
    date_availability = fields.Date(copy=False, default=lambda self: date.today() + timedelta(days=90))
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        string='Orientation',
        selection=[('north', "North"), ('south', "South"), ('east', "East"), ('west', "West")])
    active = fields.Boolean(default=True)
    buyer_id = fields.Many2one('res.partner')
    salesperson_id = fields.Many2one('res.users', copy=False, default=lambda self: self.env.user)
    tag_ids = fields.Many2many('estate.property.tag')
    offer_ids = fields.One2many('estate.property.offer', 'property_id')
    total_area = fields.Float(compute='_compute_total_area')
    best_price = fields.Monetary(compute='_compute_best_price')

    _check_expected_price = models.Constraint("CHECK(expected_price > 0)", "The expected price must be strictly positive")
    _check_selling_price = models.Constraint('CHECK(selling_price >= 0)', "The selling price must be positive")

    @api.depends('garden_area', 'living_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids')
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(o.price for o in record.offer_ids) if record.offer_ids else 0

    @api.depends('selling_price', 'commission_rate')
    def _compute_commission_amount(self):
        for record in self:
            record.commission_amount = record.selling_price * record.commission_rate / 100

    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.name} ({record.postcode or 'no postcode'})"

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = None
            self.garden_orientation = None

    @api.ondelete(at_uninstall=False)
    def _unlink_check_status(self):
        for record in self:
            if record.state not in ['new', 'cancelled']:
                raise UserError(_("A property can only be deleted if its state is 'New' or 'Cancelled'"))

    def action_property_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError(_("A sold property cannot be cancelled."))
            record.state = 'cancelled'
        return True

    def action_property_sold(self):
        for record in self:
            if record.state == 'cancelled':
                raise UserError(_("A cancelled property cannot be sold."))
            if not record.offer_ids:
                raise UserError(_("A property with no offers cannot be sold."))
            if not record.buyer_id or not record.best_price > 0 or not any(o for o in record.offer_ids if o.status == "accepted"):
                raise UserError(_("A property with no accepted offer cannot be sold"))
            record.state = 'sold'
        return True
