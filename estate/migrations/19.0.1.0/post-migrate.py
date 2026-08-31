from odoo.upgrade import util

def migrate(cr, version):
    util.remove_view(cr, "estate.estate_property_type_view_form_legacy_extension")