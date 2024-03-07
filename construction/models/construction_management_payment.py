from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ConstructionManagementPayment(models.Model):
    _name = "construction.management.payment"
    _description = "Construction Management Payment"

    name = fields.Char(
        string="Payment Reference",
        required=True,
        readonly=True,
        compute="_compute_name",
    )
    amount = fields.Float(string="Amount", required=True)
    account_number = fields.Integer(string="Account Number", required=True)
    date = fields.Date(
        string="Payment Date", default=fields.Date.today(), readonly=True
    )
    construction_id = fields.Many2one(
        "construction.management", string="Construction", required=True
    )
    
    @api.constrains("amount")
    def _check_amount(self):
        for payment in self:
            if payment.amount > payment.construction_id.pending_amount:
                raise ValidationError("Payment amount cannot exceed pending amount.")
                
    @api.depends("construction_id.contractor_id")
    def _compute_name(self):
        for record in self:
            if record.construction_id.contractor_id:
                record.name = record.construction_id.contractor_id.name
