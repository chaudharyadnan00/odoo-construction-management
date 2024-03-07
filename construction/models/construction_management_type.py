from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ConstructionManagementType(models.Model):
    _name = "construction.management.type"
    _description = "Construction Management Type"

    name = fields.Char(string="Name", required=True)
    construction_ids = fields.One2many(
        "construction.management", "construction_type_id", string="Construction Ids"
    )
    sequence=fields.Integer(string="Sequence")
