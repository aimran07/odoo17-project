from odoo import fields, models, _


class HillServiceType(models.Model):
    _name = 'hill.service.type'
    _description = 'Service Type'
    _order = 'client_type, sequence, name'

    name = fields.Char(
        string='Service Type',
        required=True,
    )
    code = fields.Char(
        string='Code',
        required=True,
    )
    client_type = fields.Selection(
        [('b2b', 'B2B'), ('b2c', 'B2C')],
        string='Client Type',
        required=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    visit_required = fields.Boolean(
        string='Visit Required',
        default=False,
    )

    _sql_constraints = [
        ('code_uniq', 'unique(code)', _('Service Type code must be unique.')),
    ]
