/*
*  Expenses © 2024
*  Author:  Ameen Ahmed
*  Company: Level Up Marketing & Software Development Services
*  Licence: Please refer to LICENSE file
*/


frappe.provide('frappe.listview_settings');


frappe.listview_settings['Expenses Entry'] = {
    onload: function(list) {
        frappe.exp().on('ready change', function() { this.setup_list(list); });
    },
    formatters: {
        payment_reference: function(v) { return cstr(v); },
        clearance_date: function(v) { return cstr(v); },
    },
};