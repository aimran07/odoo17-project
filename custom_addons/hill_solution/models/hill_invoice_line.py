from odoo import fields, models


class HillInvoiceLine(models.Model):
    _name = "hill.invoice.line"
    _description = "Hill Invoice Line"
    _order = "id"

    invoice_id = fields.Many2one(
        "hill.invoice",
        string="Invoice",
        required=True,
        ondelete="cascade",
    )

    case_id = fields.Many2one(
        "hill.case",
        string="Case",
        readonly=True,
    )

    case_number = fields.Char(
        string="Case Number",
        readonly=True,
    )

    service_type = fields.Many2one(
        'hill.service.type',
        string="Service Type",
        readonly=True,
    )

    amount = fields.Monetary(
        string="Amount",
        required=True,
        currency_field="currency_id",
        readonly=True,
    )

    currency_id = fields.Many2one(
        related="invoice_id.currency_id",
        store=True,
        readonly=True,
    )
