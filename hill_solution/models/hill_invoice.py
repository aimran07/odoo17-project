from odoo import api, fields, models, _


class HillInvoice(models.Model):
    _name = "hill.invoice"
    _description = "Hill Invoice"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "create_date desc"

    name = fields.Char(
        string="Invoice Number",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("New"),
        tracking=True,
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
        tracking=True,
    )

    line_ids = fields.One2many(
        "hill.invoice.line",
        "invoice_id",
    )

    invoice_date = fields.Date(
        default=fields.Date.context_today,
        required=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    amount_total = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_total",
        store=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("generated", "Generated"),
            ("paid", "Paid"),
        ],
        default="generated",
        tracking=True,
    )

    invoice_line_ids = fields.One2many(
        "hill.invoice.line",
        "invoice_id",
        string="Invoice Lines",
    )

    attachment_id = fields.Many2one(
        "ir.attachment",
        string="Invoice PDF",
    )

    @api.depends("invoice_line_ids.amount")
    def _compute_total(self):
        for rec in self:
            rec.amount_total = sum(
                rec.invoice_line_ids.mapped("amount")
            )

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = (
                self.env["ir.sequence"].next_by_code(
                    "hill.invoice"
                )
                or _("New")
            )

        return super().create(vals)

    @api.depends("line_ids.amount")
    def _compute_total(self):
        for invoice in self:
            invoice.amount_total = sum(
                invoice.line_ids.mapped("amount")
            )

    def action_preview_invoice(self):
        self.ensure_one()

        return self.env.ref(
            "hill_solution.action_invoice_report"
        ).report_action(self)
