from odoo.exceptions import UserError

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many('estate.property', 'salesperson_id')

    def unlink(self):
        if self.env.is_superuser():
            return super().unlink()

        for user in self:
            if user == self.env.ref("base.user_admin"):
                raise UserError("Don't delete the admin you fools!")
