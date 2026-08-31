from odoo import models, _
from odoo.exceptions import UserError


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    def _force_cancel(self, reason, msg_subtype="mail.mt_comment"):
        res = super()._force_cancel(reason, msg_subtype=msg_subtype)
        for rec in self:
            message_body = _("%(user)s canceled leave of %(target)s. Reason: %(reason)s", user=self.env.user._get_html_link(), target=rec.user_id._get_html_link(), reason=reason)
            self.env.user.employee_id.message_post(
                body=message_body,
                subtype_id=self.env.ref(msg_subtype).id
            )

        return res
