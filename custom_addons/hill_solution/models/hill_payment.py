from odoo import models, fields


class HillPayment(models.Model):
    _name = 'hill.payment'
    _description = 'Hill Payment'
    _order = 'payment_date desc, id desc'

    case_id = fields.Many2one('hill.case', string='Case', required=True, ondelete='cascade')
    amount = fields.Monetary(string='Amount', required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    payment_date = fields.Date(string='Payment Date', required=True, default=fields.Date.today)
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('check', 'Check'),
        ('card', 'Credit Card'),
    ], string='Payment Method', required=True, default='bank')
    reference = fields.Char(string='Reference')
    notes = fields.Text(string='Notes')
