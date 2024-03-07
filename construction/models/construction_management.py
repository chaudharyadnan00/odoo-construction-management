from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class ConstructionManagement(models.Model):
    _name = "construction.management"
    _description = "Construction Management"
    _order = "id desc"

    contract_id = fields.Char(readonly=True)
    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
    address = fields.Text(string="Address")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")

    tenure = fields.Integer(string="Tenure (months)", required=True)

    start_date = fields.Date(string="Start Date", readonly=True)
    end_date = fields.Date(string="End Date", readonly=True)
    client_budget = fields.Float(string="Client Budget", required=True)
    contractor_budget = fields.Float(
        string="Contractor Budget", readonly=True, copy=False
    )
    living_area = fields.Integer(string="Living Area (sqm)")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Gareden Area (sqm)")
    garden_orientation = fields.Selection(
        [("north", "North"), ("east", "East"), ("west", "West"), ("south", "South")],
        string="Garden Orientation",
    )
    total_area = fields.Integer(
        string="Total Area (in sqm)", readonly=True, compute="_compute_total_area"
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("execution", "Execution"),
            ("completed", "Completed"),
            ("failure", "Failure"),
        ],
        string="Status",
        default="new",
        copy=False,
        required=True,
    )
    pending_amount = fields.Float(
        string="Pending Amount", compute="_compute_pending_amount"
    )
    client_id = fields.Many2one(
        "res.partner", string="Client", default=lambda self: self.env.user
    )
    contractor_id = fields.Many2one("res.partner", string="Contractor", copy=False)
    image = fields.Binary(string="Images")

    construction_type_id = fields.Many2one(
        "construction.management.type", string="Construction Type"
    )

    construction_contractor_id = fields.Many2one(
        "construction.management.contractor", string="Contractor"
    )
    
    tag_ids = fields.Many2many(
        "construction.management.tag", string="Construction Tags"
    )

    offer_ids = fields.One2many(
        "construction.management.offer", "construction_id", string="Offers"
    )

    payment_ids = fields.One2many(
        "construction.management.payment", "construction_id", string="Payments"
    )

    _sql_constraints = [
        (
            "positive_client_budget",
            "CHECK(client_budget > 0)",
            "Client Budget must be strictly positive",
        ),
        (
            "positive_contractor_budget",
            "CHECK(contractor_budget >= 0)",
            "Contractor Budget must be non-negative",
        ),
    ]

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10.0
            self.garden_orientation = "north"
        else:
            self.garden_area = 0.0
            self.garden_orientation = ""

    @api.depends("payment_ids.amount", "contractor_budget")
    def _compute_pending_amount(self):
        for recrod in self:
            total_payments = sum(recrod.payment_ids.mapped("amount"))
            recrod.pending_amount = recrod.contractor_budget - total_payments

    @api.depends("garden_area", "living_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area

    @api.model
    def create(self, vals):
        if "email" in vals:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", vals["email"]):
                raise ValidationError("Invalid email format!")
        if "phone" in vals:
            if not re.match(r"^\d{10}$", vals["phone"]):
                raise ValidationError("Invalid phone number format!")
        return super().create(vals)

    def construction_management_action_complete(self):
        for record in self:
            if record.state == "failure":
                raise UserError("Failed project cannot be completed.")
            else:
                record.state = "completed"
        return True

    def construction_management_action_fail(self):
        for record in self:
            if record.state == "completed":
                raise UserError("Completed project cannot be failed")
            else:
                record.state = "failure"
        return True

    @api.model
    def create(self, vals):
        seq_value = self.env["ir.sequence"].next_by_code(
            "construction.management.contract_id"
        )
        vals["contract_id"] = seq_value
        return super().create(vals)
