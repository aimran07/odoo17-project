from odoo import fields, models


class InvoiceGenerationWizardLine(models.TransientModel):
    _name = "invoice.generation.wizard.line"
    _description = "Invoice Generation Wizard Line"

    wizard_id = fields.Many2one(
        "invoice.generation.wizard",
        required=True,
        ondelete="cascade",
    )

    selected = fields.Boolean(
        default=True,
    )

    case_id = fields.Many2one(
        "hill.case",
        readonly=True,
    )

    case_number = fields.Char(
        readonly=True,
    )

    service_type = fields.Many2one(
        "hill.service.type",
        related="case_id.service_type",
        readonly=True,
    )

    amount = fields.Monetary(
        readonly=True,
        currency_field="currency_id",
    )

    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )
