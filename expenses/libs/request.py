# Expenses © 2024
# Author:  Ameen Ahmed
# Company: Level Up Marketing & Software Development Services
# Licence: Please refer to LICENSE file


import frappe
from frappe.utils import has_common

from .cache import get_cached_doc
from .check import get_count
from .common import parse_json
from .expense import (
    get_expenses_for_company,
    set_expenses_restored,
    set_expenses_requested,
    set_expenses_approved,
    set_expenses_rejected,
    get_expenses
)


## [Install, Internal]
__REQUEST__ = "Expenses Request"


## [Internal]
__REQUEST_DETAILS__ = "Expenses Request Details"


# [Request]
RequestStatus = frappe._dict({
    "Draft": "Draft",
    "Pending": "Pending",
    "Cancelled": "Cancelled",
    "Approved": "Approved",
    "Rejected": "Rejected",
    "Processed": "Processed"
})


## [Internal]
__REQUEST_MODERATOR_ROLE__ = "Expenses Request Moderator"


## [Internal]
__REQUEST_REVIEWER_ROLE__ = "Expenses Request Reviewer"
_REQUEST_SUPER_ROLES_ = [
    "Expenses Reviewer",
    "Accounts Manager",
    "System Manager",
    "Administrator"
]


## [Expense]
def get_expense_requests(expense: str):
    doc = frappe.qb.DocType(__REQUEST__)
    ddoc = frappe.qb.DocType(__REQUEST_DETAILS__)
    data = (
        frappe.qb.from_(ddoc)
        .select(doc.name)
        .left_join(doc)
        .on(doc.name == ddoc.parent)
        .where(ddoc.expense == expense)
        .where(ddoc.parenttype == __REQUEST__)
        .where(ddoc.parentfield == "expenses")
    ).run(as_dict=True)
    
    if not data or not isinstance(data, list):
        return None
    
    return data


# [Request]
def is_company_expenses(expenses: list, company: str):
    data = get_expenses_for_company(expenses, company)
    if not data or len(data) != len(expenses):
        return False
    
    return True


# [Request]
def is_request_amended(name: str):
    return get_count(__REQUEST__, {"amended_from": name}) > 0


# [Request]
def restore_expenses(expenses: list):
    set_expenses_restored(expenses)


# [Request]
def request_expenses(expenses: list):
    set_expenses_requested(expenses)


# [Request]
def approve_expenses(expenses: list):
    set_expenses_approved(expenses)


# [Request]
def reject_expenses(expenses: list):
    set_expenses_rejected(expenses)


# [Request Form]
@frappe.whitelist()
def request_form_setup():
    return {
        "is_moderator": is_request_moderator(),
        "is_reviewer": is_request_reviewer(),
    }


# [Request, Internal]
def is_request_moderator():
    return 1 if __REQUEST_MODERATOR_ROLE__ in frappe.get_roles() else 0


# [Request, Internal]
def is_request_reviewer():
    return 1 if __REQUEST_REVIEWER_ROLE__ in frappe.get_roles() else 0


# [Request Form]
@frappe.whitelist(methods=["POST"])
def get_expenses_data(expenses):
    if isinstance(expenses, str):
        expenses = parse_json(expenses)
    
    if not expenses or not isinstance(expenses, list):
        return []
    
    return get_expenses([str(v) for v in expenses])


# [Request Form]
@frappe.whitelist()
def search_company_expenses(
    doctype, txt, searchfield, start, page_len, filters, as_dict=False
):
    if (
        not filters or
        not getattr(filters, "company", "") or
        not isinstance(filters.get("company"), str)
    ):
        return []
    
    company = filters.get("company")
    existing = None
    date = None
    if (
        getattr(filters, "existing", "") and
        isinstance(filters.get("existing"), (str, list))
    ):
        existing = filters.get("existing")
        if isinstance(existing, str):
            existing = parse_json(existing)
        if existing and isinstance(existing, list):
            existing = [str(v) for v in existing]
        else:
            existing = None
    
    if (
        getattr(filters, "date", "") and
        isinstance(filters.get("date"), str)
    ):
        date = filters.get("date")
    
    if not txt or not isinstance(txt, str):
        txt = None
    
    return search_expenses_by_company(
        company, txt, existing, date, as_dict
    )


# [Request Form]
@frappe.whitelist(methods=["POST"])
def reject_request(name, reason):
    if (
        not name or not isinstance(name, str) or
        not isinstance(reason, str)
    ):
        return 0
    
    doc = get_cached_doc(__REQUEST__, name)
    if not doc:
        return 0
    
    doc.add_comment(
        "Workflow",
        reason,
        doc.owner,
        comment_by=frappe.session.user
    )
    
    return 1


## [Entry]
def get_request(name: str):
    doc = get_cached_doc(__REQUEST__, name)
    
    if doc.status != RequestStatus.Approved:
        return None
    
    data = doc.as_dict()
    data["expenses"] = get_expenses([v.expense for v in doc.expenses])
    
    return data


# [Entry]
def process_request(name: str):
    get_cached_doc(__REQUEST__, name).process(ignore_permissions=True)


# [Entry]
def reject_request(name: str):
    get_cached_doc(__REQUEST__, name).reject(ignore_permissions=True)