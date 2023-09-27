# Expenses © 2023
# Author:  Ameen Ahmed
# Company: Level Up Marketing & Software Development Services
# Licence: Please refer to LICENSE file


import frappe
from frappe import _

from .attachment import get_attachments_by_parents
from .common import (
    error,
    log_error,
    parse_json
)
from .search import filter_search, prepare_data


# Expense Item
def expenses_of_item_exists(item):
    return frappe.db.exists("Expense", {"expense_item": item})


# Expense
# Expense Form
# Expense List
# Expense Entry
# Expense Entry Form
@frappe.whitelist()
def with_expense_claim():
    return 1 if frappe.db.exists("DocType", "Expense Claim") else 0


# Internal
_EXPENSE_FIELDS_ = [
    "company",
    "expense_item",
    "expense_account",
    "required_by",
    "description",
    "project",
    "currency",
    "cost",
    "qty",
    "total",
    "is_advance",
    "is_paid",
    "paid_by",
    "expense_claim",
    "party_type",
    "party",
    "attachments",
]


# Expense List
@frappe.whitelist(methods=["POST"])
def add_expense(data):
    if data:
        data = parse_json(data)
    
    if not data or not isinstance(data, dict):
        return 0
    
    data = {k:v for k, v in data.items() if k in _EXPENSE_FIELDS_}
    
    try:
        (frappe.new_doc("Expense")
            .update(data)
            .insert(ignore_permissions=True, ignore_mandatory=True))
    except Exception as exc:
        log_error(exc)
        return 0
    
    return 1


# Expenses Request
def is_expenses_belongs_to_company(names, company):
    if (
        not names or not isinstance(names, list) or
        not company or not isinstance(company, str)
    ):
        return False
    
    data = frappe.get_all(
        "Expense",
        fields=["name"],
        filters={
            "name": ["in", names],
            "company": company,
            "docstatus": ["!=", 2],
        },
        pluck="name"
    )
    
    return len(data) == len(names)


# Expenses Request Form (MultiSelect Dialog)
@frappe.whitelist()
def search_company_expenses(
    doctype, txt, searchfield, start, page_len, filters, as_dict=False
):
    if not filters or not isinstance(filters.get("company"), str):
        return []
    
    dt = "Expense"
    doc = frappe.qb.DocType(dt)
    qry = (frappe.qb.from_(doc)
        .select(
            doc.name,
            doc.expense_item,
            doc.description,
            doc.total,
            doc.is_advance,
            doc.required_by
        )
        .where(doc.company == filters.get("company"))
        .where(doc.is_requested == 0)
        .where(doc.owner == frappe.session.user)
        .where(doc.docstatus != 2))
    
    qry = filter_search(doc, qry, dt, txt, doc.name, "name")
    
    if (existing := filters.get("existing")):
        existing = parse_json(existing)
        
        if existing and isinstance(existing, list):
            qry = qry.where(doc.name.notin(existing))
    
    if (date := filters.get("date")):
        if isinstance(date, str):
            qry = qry.where(doc.required_by.lte(date))
    
    data = qry.run(as_dict=as_dict)
    
    data = prepare_data(data, dt, "name", txt, as_dict)
    
    return data


# Expenses Request
def reserve_request_expenses(expenses):
    doc = frappe.qb.DocType("Expense")
    (
        frappe.qb.update(doc)
        .set(doc.is_requested, 1)
        .where(doc.name.isin(expenses))
        .where(doc.is_requested == 0)
        .where(doc.docstatus != 2)
    ).run()


# Expenses Request
def release_request_expenses(expenses):
    doc = frappe.qb.DocType("Expense")
    (
        frappe.qb.update(doc)
        .set(doc.is_requested, 0)
        .set(doc.is_approved, 0)
        .where(doc.name.isin(expenses))
        .where(doc.is_requested == 1)
        .where(doc.docstatus != 2)
    ).run()


# Expenses Request
def approve_request_expenses(expenses):
    doc = frappe.qb.DocType("Expense")
    (
        frappe.qb.update(doc)
        .set(doc.is_approved, 1)
        .where(doc.name.isin(expenses))
        .where(doc.is_requested == 1)
        .where(doc.is_approved == 0)
        .where(doc.docstatus != 2)
    ).run()


# Expenses Request Form
# Self Request
@frappe.whitelist(methods=["POST"])
def get_expenses_data(expenses):
    if isinstance(expenses, str):
        expenses = parse_json(expenses)
    
    if not expenses or not isinstance(expenses, list):
        return []
    
    expenses = [str(v) for v in expenses]
    
    doc = frappe.qb.DocType("Expense")
    data = (
        frappe.qb.from_(doc)
        .select(
            doc.name,
            doc.company,
            doc.expense_account,
            doc.required_by,
            doc.description,
            doc.currency,
            doc.total,
            doc.is_paid,
            doc.paid_by,
            doc.is_advance,
            doc.party_type,
            doc.party,
            doc.project
        )
        .where(doc.name.isin(expenses))
        .where(doc.is_requested == 1)
        .where(doc.owner == frappe.session.user)
        .where(doc.docstatus != 2)
    ).run(as_dict=True)
    
    if not data or not isinstance(data, list):
        error(_("Unable to get the data of the expenses"))
    
    if (attachments := get_attachments_by_parents(
        [v["name"] for v in data],
        "Expense",
        "attachments"
    )):
        for i in range(len(data)):
            if data[i]["name"] in attachments:
                data[i]["attachments"] = attachments.get(data[i]["name"])
    
    return data