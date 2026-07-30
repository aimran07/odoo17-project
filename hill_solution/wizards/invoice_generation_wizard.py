from odoo import api, fields, models
from odoo.exceptions import UserError

class InvoiceGenerationWizard(models.TransientModel):
    _name = "invoice.generation.wizard"
    _description = "Generate Invoice Wizard"

    partner_id = fields.Many2one(
        "res.partner",
        required=True,
        readonly=True,
    )

    line_ids = fields.One2many(
        "invoice.generation.wizard.line",
        "wizard_id",
        string="Cases",
    )

    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )

    amount_total = fields.Monetary(
        compute="_compute_total",
        currency_field="currency_id",
    )

    @api.depends("line_ids.selected", "line_ids.amount")
    def _compute_total(self):
        for wizard in self:
            wizard.amount_total = sum(
                wizard.line_ids.filtered("selected").mapped("amount")
            )

    def action_generate_invoice(self):
        self.ensure_one()

        selected_lines = self.line_ids.filtered("selected")

        if not selected_lines:
            raise UserError("Please select at least one case.")

        invoice = self.env["hill.invoice"].create({
            "partner_id": self.partner_id.id,

            "line_ids": [
                (0, 0, {
                    "case_id": line.case_id.id,
                    "case_number": line.case_number,
                    "service_type": line.case_id.service_type,
                    "amount": line.amount,
                })
                for line in selected_lines
            ]
        })

        for line in selected_lines:
            line.case_id.write({
                "invoice_status": "invoiced",
                "invoice_id": invoice.id,
            })

        return {
            "type": "ir.actions.act_window",
            "res_model": "hill.invoice",
            "res_id": invoice.id,
            "view_mode": "form",
            "target": "current",
        }
