# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Estate',
    'depends': [
        'mail',
        'hr_holidays',
    ],
    'version': '16.0.1.0.0',
    'author': "Odoo S.A.",
    'license': "LGPL-3",
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'estate/static/src/js/legacy_property_widget.js',
        ],
    },
    'data': [
        'views/res_users_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'security/ir.model.access.csv',
    ],
}
