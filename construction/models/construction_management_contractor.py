from odoo import models, fields


class ConstructionManagementContractor(models.Model):
    _name = "construction.management.contractor"
    _description = "Contractors in Construction Management"

    name = fields.Char(string="Contractor Name", default="Adnan")
    # construction_ids = fields.One2many(
    #     "construction.management",
    #     "construction_contractor_id",
    #     string="Construction Ids",
    # )
    sequence = fields.Integer(string="Sequence")
