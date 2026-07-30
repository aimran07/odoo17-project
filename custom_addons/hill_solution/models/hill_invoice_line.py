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

    service_type = fields.Selection(
        [('ndd', 'NDD'),
         ('heat_destratifier', 'Heat destratifier'),
         ('led_study', 'LED study'),
         ('study_163', 'Study 163'),
         ('regulatory_audit', 'Regulatory audit'),
         ('sizing_171', 'Sizing 171'),
         ('study_174', 'Study 174'),
         ('study_175', 'Study 175'),
         ('study_179', 'Study 179')],
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
