# Expenses © 2024
# Author:  Ameen Ahmed
# Company: Level Up Marketing & Software Development Services
# Licence: Please refer to LICENSE file


app_name = "expenses"
app_title = "Expenses"
app_publisher = "Ameen Ahmed (Level Up)"
app_description = "An expenses management module for ERPNext."
app_icon = "octicon octicon-note"
app_color = "blue"
app_email = "kid1194@gmail.com"
app_license = "MIT"


doctype_js = {
    "Expenses Settings": "public/js/expenses.bundle.js",
    "Expense Type": "public/js/expenses.bundle.js",
    "Expense Item": "public/js/expenses.bundle.js",
    "Expense": "public/js/expenses.bundle.js",
    "Expenses Request": "public/js/expenses.bundle.js",
    "Expenses Entry": "public/js/expenses.bundle.js",
}


doctype_list_js = {
    "Expense Item": "public/js/expenses.bundle.js",
    "Expense Type": "public/js/expenses.bundle.js",
    "Expense": "public/js/expenses.bundle.js",
    "Expenses Request": "public/js/expenses.bundle.js",
    "Expenses Entry": "public/js/expenses.bundle.js",
}


after_install = "expenses.setup.install.after_install"
before_uninstall = "expenses.setup.uninstall.before_uninstall"


fixtures = [
    "Role",
    "Workflow",
    "Workflow State",
    "Workflow Action Master"
]


scheduler_events = {
    "daily": [
        "expenses.libs.update.auto_check"
    ]
}


treeviews = [
    "Expense Type"
]