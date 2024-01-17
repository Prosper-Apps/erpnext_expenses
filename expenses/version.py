# Expenses © 2024
# Author:  Ameen Ahmed
# Company: Level Up Marketing & Software Development Services
# Licence: Please refer to LICENSE file


from frappe import __version__


__frappe_version__ = int(__version__.split(".")[0])
__frappe_mv15__ = __frappe_version__ > 14
__frappe_v14__ = __frappe_version__ == 14
__frappe_v13__ = __frappe_version__ == 13