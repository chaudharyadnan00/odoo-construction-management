{
    "name": "Construction Management",
    "version": "0.1",
    "depends": ["base"],
    "author": "adch@odoo.com",
    "category": "Localization",
    "description": """
    The One and Only Best Construction Management Availble on Odoo!
    """,
    "installable": True,
    "application": True,
    "auto_install": False,
    "data": [
        "security/ir.model.access.csv",
        "data/construction_management_sequence.xml",
        "views/construction_management_contractor_views.xml",
        "views/construction_management_payment_views.xml",
        "views/construction_management_offer_views.xml",
        "views/construction_management_tag_views.xml",
        "views/construction_management_type_views.xml",
        "views/construction_management_views.xml",
        "views/construction_menus.xml",
    ],
    "license": "LGPL-3",
}
