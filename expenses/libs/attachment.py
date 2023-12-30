# Expenses © 2024
# Author:  Ameen Ahmed
# Company: Level Up Marketing & Software Development Services
# Licence: Please refer to LICENSE file


import frappe

from .background import enqueue_job
from .common import parse_json


## [Internal]
_EXPENSE_ATTACH_ = "Expense Attachment"


## [Internal]
_FILE_ = "File"


# [Entry, Entry Form, Expense, Expense Form]
@frappe.whitelist(methods=["POST"])
def delete_attach_files(doctype, name, files):
    if (
        not doctype or not isinstance(doctype, str) or
        not name or not isinstance(name, str) or
        not files or (
            not isinstance(files, str) and
            not isinstance(files, list)
        )
    ):
        return 0
    
    files = parse_json(files)
    if not files or not isinstance(files, list):
        return 0
    
    if (file_names := frappe.get_all(
        _FILE_,
        fields=["name"],
        filters=[
            ["file_url", "in", files],
            ["attached_to_doctype", "=", doctype],
            ["ifnull(`attached_to_name`,\"\")", "in", [name, ""]]
        ],
        pluck="name"
    )):
        enqueue_job(
            "expenses.libs.attachment.files_delete",
            f"exp-files-delete-{name}",
            files=file_names
        )
    
    return 1


## [Internal]
def files_delete(files: list):
    for file in files:
        frappe.get_doc(_FILE_, file).delete(ignore_permissions=True)


## [Expense]
def get_files_by_parents(parents: list, parent_type: str, parent_field: str):
    data = frappe.get_all(
        _EXPENSE_ATTACH_,
        fields=["parent", "file", "description"],
        filters=[
            [_EXPENSE_ATTACH_, "parent", "in", parents],
            [_EXPENSE_ATTACH_, "parenttype", "=", parent_type],
            [_EXPENSE_ATTACH_, "parentfield", "=", parent_field]
        ]
    )
    
    if not data or not isinstance(data, list):
        return None
    
    groups = {}
    for v in data:
        k = v["parent"]
        if k not in groups:
            groups[k] = []
        
        groups[k].append({
            "file": v["file"],
            "description": v["description"],
        })
    
    return groups