from odoo import fields, models
from random import randint

class PropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = "Test description for estate.property.tag model"
    _order = 'name'

    def _get_default_color(self):
        return randint(1, 11)


    name = fields.Char(required=True)
    color = fields.Integer(default=_get_default_color)

    _check_name = models.Constraint('UNIQUE (name)', "Property tag name must be unique)")
