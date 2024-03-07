from odoo import models, fields


class EstatePropertyTag(models.Model):
    _name = "construction.management.tag"
    _description = "Construction Management Tag"
    _order = "name"

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color")

    _sql_constraints = [
        (
            "unique_name",
            "UNIQUE(name)",
            "Tag name must be unique",
        ),
    ]
