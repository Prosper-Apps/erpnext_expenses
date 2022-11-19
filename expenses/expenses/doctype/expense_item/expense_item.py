# ERPNext Expenses © 2022
# Author:  Ameen Ahmed
# Company: Level Up Marketing & Software Development Services
# Licence: Please refer to LICENSE file


import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document

from expenses.utils import (
    error,
    get_cached_value,
    clear_document_cache,
    expenses_of_item_exists
)


class ExpenseItem(Document):
    def before_validate(self):
        if self.expense_accounts:
            existing = []
            for i in range(len(self.expense_accounts)):
                v = self.expense_accounts[i]
                if not v.company or v.company in existing:
                    self.expense_accounts.remove(v)
                else:
                    existing.append(v.company)
                    for k in ["cost", "qty"]:
                        min_k = "min_" + k
                        max_k = "max_" + k
                        val = flt(v[k])
                        if val != 0:
                            if val < 0:
                                v[k] = 0
                            v[min_k] = 0
                            v[max_k] = 0
                        else:
                            min_val = flt(v[min_k])
                            max_val = flt(v[max_k])
                            if max_val < 0:
                                v[max_k] = 0
                            if min_val < 0 or min_val > max_val:
                                v[min_k] = 0
    
    
    def validate(self):
        if not self.item_name:
            error(_("The name is mandatory"))
        if frappe.db.exists(self.doctype, self.item_name):
            error(_("{0} already exist").format(self.item_name))
        if not self.expense_type:
            error(_("The expense type is mandatory"))
        
        self.validate_accounts()
    
    
    def validate_accounts(self):
        if self.expense_accounts:
            for v in self.expense_accounts:
                if v.account and get_cached_value("Account", v.account, "company") != v.company:
                    error(
                        (_("The expense account \"{0}\" does not belong to the company \"{1}\"")
                            .format(v.account, v.company))
                    )
    
    
    def before_save(self):
        self.load_doc_before_save()
        clear_document_cache(
            self.doctype,
            self.name if not self.get_doc_before_save() else self.get_doc_before_save().name
        )
    
    
    def on_trash(self):
        if expenses_of_item_exists(self.name):
            error(_(
                ("{0} cannot be removed before removing its reference in Expense doctype"
                    .format(self.doctype))
            ))