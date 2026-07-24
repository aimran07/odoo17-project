from odoo import models, fields


class DemoRecord(models.Model):
    _name = "demo.record"
    _description = "Demo Record"

    name = fields.Char()
    email = fields.Char()
    phone = fields.Char()

    street = fields.Char()
    city = fields.Char()

    notes = fields.Text()
