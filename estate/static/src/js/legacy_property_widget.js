odoo.define('estate.legacy_property_widget', function (require) {
    'use strict';

    const Widget = require('web.Widget');

    return Widget.extend({
        template: 'estate.LegacyPropertyWidget',

        start: function () {
            return this._super.apply(this, arguments);
        },
    });
});
