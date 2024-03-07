from odoo import models, fields, api
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class ConstructionManagementOffer(models.Model):
    _name = "construction.management.offer"
    _description = "Constrcution Management Offer"
    _order = "offer_price asc"

    offer_price = fields.Float(string="Price")
    status = fields.Selection(
        [("accepted", "Accepted"), ("refused", "Refused")], string="Status", copy=False
    )
    partner_id = fields.Many2one("res.partner", required=True, string="Partner")
    expected_start_date = fields.Date(string="Expected Start Date",compute="_compute_expected_start_date")
    offer_deadline = fields.Date(
        string="Deadline",
        compute="_compute_offer_deadline",
        inverse="_inverse_offer_deadline",
    )
    validity = fields.Integer(string="Validity", default=7)
    construction_id = fields.Many2one(
        "construction.management", required=True, string="Constrcution Id"
    )

    _sql_constraints = [
        (
            "positive_price",
            "CHECK(offer_price > 0)",
            "An offer price must be strictly positive",
        ),
    ]
    @api.model
    def create(self, vals):
        offer = super().create(vals)
        offer.construction_id.state="offer_received"
        existing_offers = self.search(
            [("construction_id", "=", offer.construction_id.id), ("id", "!=", offer.id)]
        )
        for record in existing_offers:
            if offer.offer_price > record.offer_price:
                raise ValidationError("Offer Price should be smaller than existing offers")
        return offer

    def unlink(self):
        construction_ids = self.mapped("construction_id")
        super().unlink()
        for record in construction_ids:
            remaining_offers = self.env["construction.management.offer"].search(
                [("construction_id", "=", record.id)]
            )
            if not remaining_offers:
                record.state = "new"

    @api.depends("create_date", "validity")
    def _compute_offer_deadline(self):
        for record in self:
            if record.create_date:
                record.offer_deadline = record.create_date + timedelta(days=record.validity)
            else:
                record.offer_deadline = date.today() + timedelta(days=record.validity)

    def _inverse_offer_deadline(self):
        for record in self:
            if record.create_date and record.offer_deadline:
                record.validity = (fields.Date.from_string(record.offer_deadline) - fields.Date.from_string(record.create_date)).days

    @api.depends("offer_deadline")
    def _compute_expected_start_date(self):
        for record in self:
            if record.offer_deadline:
                record.expected_start_date = record.offer_deadline + timedelta(days=7)

    def construction_management_offer_action_accept(self):
        for record in self:
            if record.construction_id.contractor_budget != 0.0:
                raise UserError("Can not accept more than one offer")
            else:
                construction_id = record.construction_id
                construction_offers = self.env["construction.management.offer"].search(
                    [
                        ("id", "!=", record.id),
                        ("construction_id", "=", construction_id.id),
                    ]
                )
                construction_offers.write({"status": "refused"})
                record.status = "accepted"
                construction_id.state = "offer_accepted"
                construction_id.contractor_budget = record.offer_price
                construction_id.contractor_id = record.partner_id
                construction_id.start_date = record.expected_start_date
                construction_id.end_date = record.expected_start_date + timedelta(days = 30 * construction_id.tenure)
        return True

    def construction_management_offer_action_refuse(self):
        for record in self:
            record.status = "refused"
            record.construction_id.contractor_budget = 0.0
            record.construction_id.contractor_id = False
            record.construction_id.start_date=""
            record.construction_id.end_date = ""
        return True
