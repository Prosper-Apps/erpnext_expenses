# Expenses © 2024
# Author:  Ameen Ahmed
# Company: Level Up Marketing & Software Development Services
# Licence: Please refer to LICENSE file


import frappe


# [EXP Entry, EXP Entry Form, EXP Expense, EXP Expense Form]
@frappe.whitelist(methods=["POST"])
def delete_attach_files(doctype, name, files):
    if (
        not doctype or not isinstance(doctype, str) or
        not name or not isinstance(name, str) or
        not files or not isinstance(files, (str, list))
    ):
        return 0
    
    from .common import parse_json
    
    files = parse_json(files)
    if not files or not isinstance(files, list):
        return 0
    
    file_names = frappe.get_all(
        "File",
        fields=["name"],
        filters=[
            ["file_url", "in", files],
            ["attached_to_doctype", "=", doctype],
            ["ifnull(`attached_to_name`,\"\")", "in", [name, ""]]
        ],
        pluck="name",
        ignore_permissions=True,
        strict=False
    )
    if file_names and isinstance(file_names, list):
        from .background import enqueue_job
        
        enqueue_job(
            "expenses.libs.attachment.files_delete",
            f"exp-files-delete-{name}",
            files=file_names
        )
    
    return 1


# [Internal]
def files_delete(files: list):
    for file in files:
        frappe.get_doc("File", file).delete(ignore_permissions=True)


# [Expense]
def get_files_by_parents(parents: list, parent_type: str, parent_field: str):
    dt = "Expense Attachment"
    data = frappe.get_all(
        dt,
        fields=["parent", "file", "description"],
        filters=[
            [dt, "parent", "in", parents],
            [dt, "parenttype", "=", parent_type],
            [dt, "parentfield", "=", parent_field]
        ],
        ignore_permissions=True,
        strict=False
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
            "description": v["description"]
        })
    
    return groups