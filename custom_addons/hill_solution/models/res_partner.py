from datetime import timedelta

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    hill_client_type = fields.Selection(
        [('b2b', 'B2B'), ('b2c', 'B2C')],
        string='Client Type',
    )

    # B2B fields
    hill_company_name = fields.Char(string='Company Name')
    hill_contact_firstname = fields.Char(string='Contact First Name')
    hill_contact_lastname = fields.Char(string='Contact Last Name')
    hill_b2b_phone = fields.Char(string='Phone Number')
    hill_siret = fields.Char(string='SIRET Number')

    # B2C fields
    hill_beneficiary_firstname = fields.Char(string='Beneficiary First Name')
    hill_beneficiary_lastname = fields.Char(string='Beneficiary Last Name')
    hill_beneficiary_phone = fields.Char(string='Phone Number')
    hill_beneficiary_status = fields.Selection(
        [('high_vulnerability', 'High-Vulnerability (Extreme Hardship)'),
         ('vulnerable', 'Vulnerable (Hardship)'),
         ('standard', 'Standard')],
        string='Beneficiary Status',
    )

    hill_requires_advance_payment = fields.Boolean(
        string='Requires Advance Payment',
    )


    invoice_case_count = fields.Integer(
        string="Open Cases",
        compute="_compute_invoice_details",
    )

    invoice_total_amount = fields.Monetary(
        string="Total Amount",
        compute="_compute_invoice_details",
        currency_field="currency_id",
    )

    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )

    def _compute_invoice_details(self):
        invoice_stage = self.env.ref(
            "hill_solution.stage_invoice_payment",
            raise_if_not_found=False,
        )

        for partner in self:
            cases = self.env["hill.case"].search([
                ("partner_id", "=", partner.id),
                ("invoice_status", "=", "not_invoiced"),
                ("stage_id", "=", invoice_stage.id if invoice_stage else False),
            ])

            partner.invoice_case_count = len(cases)
            partner.invoice_total_amount = sum(cases.mapped("amount_total"))

    @api.model
    def action_invoice_customers(self):
        invoice_stage = self.env.ref(
            "hill_solution.stage_invoice_payment",
            raise_if_not_found=False,
        )

        case_domain = [
            ("invoice_status", "=", "not_invoiced"),
            ("stage_id", "=", invoice_stage.id),
            ("partner_id", "!=", False),
        ]

        partner_ids = self.env["hill.case"].search(case_domain).mapped("partner_id").ids

        return {
            "type": "ir.actions.act_window",
            "name": _("Invoices"),
            "res_model": "res.partner",
            "view_mode": "tree",
            "view_id": self.env.ref(
                "hill_solution.view_partner_invoice_tree"
            ).id,
            "domain": [
                ("id", "in", partner_ids),
                ("user_ids.share", "=", True),
            ],
            "context": {
                "create": False,
                "edit": False,
                "delete": False,
            },
        }

    def action_open_invoice_wizard(self):
        self.ensure_one()

        invoice_stage = self.env.ref(
            "hill_solution.stage_invoice_payment"
        )

        case_domain = [
            ("partner_id", "=", self.id),
            ("invoice_status", "=", "not_invoiced"),
            ("stage_id", "=", invoice_stage.id),
            ("date_invoice_stage", ">=", fields.Date.today() - timedelta(days=30)),
        ]

        default_case_id = self.env.context.get('default_case_id')
        if default_case_id:
            case_domain.append(("id", "=", default_case_id))

        wizard = self.env[
            "invoice.generation.wizard"
        ].create({
            "partner_id": self.id,
        })

        cases = self.env["hill.case"].search(case_domain)

        for case in cases:
            self.env[
                "invoice.generation.wizard.line"
            ].create({
                "wizard_id": wizard.id,
                "case_id": case.id,
                "case_number": case.case_number,
                "amount": case.amount_total,
                "selected": True,
            })

        return {
            "type": "ir.actions.act_window",
            "name": _("Generate Invoice"),
            "res_model": "invoice.generation.wizard",
            "view_mode": "form",
            "res_id": wizard.id,
            "target": "new",
            "context": {
                "edit": True,
            },
        }
