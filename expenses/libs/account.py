# Expenses © 2024
# Author:  Ameen Ahmed
# Company: Level Up Marketing & Software Development Services
# Licence: Please refer to LICENSE file


from pypika.enums import Order

import frappe
from frappe.utils import flt


## [Internal]
__FIELD__ = "expense_accounts"


## [Type]
def get_types_with_accounts():
    from .cache import (
        get_cache,
        set_cache
    )
    
    dt = "Expense Type"
    key = "types-with-expense-accounts"
    data = get_cache(dt, key)
    if data and isinstance(data, list):
        return data
    
    doc = frappe.qb.DocType("Expense Type Account")
    pdoc = frappe.qb.DocType(dt)
    
    data = (
        frappe.qb.from_(doc)
        .select(doc.parent)
        .distinct()
        .left_join(pdoc)
        .on(pdoc.name == doc.parent)
        .where(doc.parenttype == dt)
        .where(doc.parentfield == __FIELD__)
        .where(pdoc.disabled == 0)
    ).run(as_dict=True)
    
    if not data or not isinstance(data, list):
        return None
    
    data = [v["parent"] for v in data]
    set_cache(dt, key, data)
    
    return data


## [Type]
def get_type_accounts(type_name: str):
    from .cache import (
        get_cached_value,
        get_cache,
        set_cache
    )
    
    dt = "Expense Type"
    key = f"{type_name}-expense-accounts"
    data = get_cache(dt, key)
    if data and isinstance(data, list):
        return data
    
    type_data = get_cached_value(dt, type_name, ["lft", "rgt"])
    
    doc = frappe.qb.DocType("Expense Type Account")
    pdoc = frappe.qb.DocType(dt)
    jdoc = frappe.qb.DocType(dt)
    adoc = frappe.qb.DocType("Account")
    
    pqry = (frappe.qb.from_(pdoc)
        .select(pdoc.name)
        .where(pdoc.disabled == 0)
        .where(pdoc.lft.lte(type_data.lft))
        .where(pdoc.rgt.gte(type_data.rgt)))
    
    data = (
        frappe.qb.from_(doc)
        .select(
            doc.company,
            doc.account,
            adoc.account_currency.as_("currency")
        )
        .left_join(jdoc)
        .on(jdoc.name == doc.parent)
        .inner_join(adoc)
        .on(adoc.name == doc.account)
        .where(doc.parent.isin(pqry))
        .where(doc.parenttype == dt)
        .where(doc.parentfield == __FIELD__)
        .orderby(jdoc.lft, order=Order.desc)
    ).run(as_dict=True)
    
    if not data or not isinstance(data, list):
        return None
    
    ret = []
    comps = []
    for i in range(len(data)):
        v = data.pop(0)
        if v["company"] not in comps:
            ret.append(v)
            comps.append(v["company"])
    
    set_cache(dt, key, ret)
    
    return ret


## [Type]
def get_type_company_account_data(parent: str, company: str):
    if (
        not parent or (
            not isinstance(parent, str) and
            not isinstance(parent, list)
        )
    ):
        return None
    
    dt = "Expense Type"
    lft, rgt = frappe.db.get_value(dt, parent, ["lft", "rgt"])
    
    pdoc = frappe.qb.DocType(dt)
    parent_qry = (frappe.qb.from_(pdoc)
        .select(pdoc.name)
        .where(pdoc.disabled == 0)
        .where(pdoc.lft.lte(lft))
        .where(pdoc.rgt.gte(rgt))
        .orderby(pdoc.lft, order=Order.desc))
    
    doc = frappe.qb.DocType("Expense Type Account")
    adoc = frappe.qb.DocType("Account")
    data = (
        frappe.qb.from_(doc)
        .select(
            doc.account,
            adoc.account_currency.as_("currency")
        )
        .left_join(pdoc)
        .on(pdoc.name == doc.parent)
        .inner_join(adoc)
        .on(adoc.name == doc.account)
        .where(doc.parent.isin(parent_qry))
        .where(doc.company == company)
        .where(doc.parenttype == dt)
        .where(doc.parentfield == __FIELD__)
        .orderby(pdoc.lft, order=Order.desc)
        .limit(1)
    ).run(as_dict=True)
    
    if not data or not isinstance(data, list):
        return None
    
    data = data.pop(0)
    return frappe._dict(data)


## [Item]
def get_item_company_account_data(parent, company: str):
    if (
        not parent or (
            not isinstance(parent, str) and
            not isinstance(parent, list)
        )
    ):
        return None
    
    doc = frappe.qb.DocType("Expense Item Account")
    adoc = frappe.qb.DocType("Account")
    data = (
        frappe.qb.from_(doc)
        .select(
            doc.account,
            adoc.account_currency.as_("currency"),
            doc.cost,
            doc.min_cost,
            doc.max_cost,
            doc.qty,
            doc.min_qty,
            doc.max_qty
        )
        .inner_join(adoc)
        .on(adoc.name == doc.account)
        .where(doc.company == company)
        .where(doc.parenttype == "Expense Item")
        .where(doc.parentfield == __FIELD__)
        .limit(1)
    )
    
    if isinstance(parent, list):
        data = data.where(doc.parent.isin(parent))
    else:
        data = data.where(doc.parent == parent)
    
    data = data.run(as_dict=True)
    
    if not data or not isinstance(data, list):
        return None
    
    data = data.pop(0)
    for k in ["cost", "qty"]:
        data[k] = flt(data[k])
        data["min_" + k] = flt(data["min_" + k])
        data["max_" + k] = flt(data["max_" + k])
    
    return frappe._dict(data)