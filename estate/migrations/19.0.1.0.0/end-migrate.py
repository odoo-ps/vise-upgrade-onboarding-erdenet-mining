from odoo.upgrade import util


def migrate(cr, version):
    util.reset_cowed_views(cr, "website_sale.header_cart_link")

    cr.execute(
        "UPDATE ir_ui_menu SET parent_id = %s WHERE id = %s",
        [util.ref(cr, "account.account_transactions_menu"), util.ref(cr, "account.menu_action_analytic_lines_tree")],
    )
    util.force_noupdate(cr, "account.menu_action_analytic_lines_tree", noupdate=False)

    # Update Deadline On Creation
    cr.execute(
        """UPDATE base_automation
              SET active = 't'
            WHERE id = 1
        """
    )

    # Activity on Delivery Date change
    cr.execute(
        """UPDATE base_automation
              SET active = 't',
                  trigger = 'on_create_or_write'
            WHERE id = 2
        """
    )

    with util.edit_view(cr, "studio_customization.odoo_studio_stock_pi_e4864fcf-c848-4684-9cc6-45243d3b3d7a") as arch:
        node = arch.xpath(".//xpath[@expr=\"//form[1]/sheet[1]/notebook[1]/page[@name='operations']/field[@name='move_ids_without_package']/list[1]/field[@name='quantity_done']\"]")[0]
        node.attrib['expr'] = "//form[1]/sheet[1]/notebook[1]/page[@name='operations']/field[@name='move_ids']/list[1]/field[@name='quantity']"
