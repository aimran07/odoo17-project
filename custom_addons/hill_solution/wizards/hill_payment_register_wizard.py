from odoo import models, fields, api, _

class HillPaymentRegisterWizard(models.TransientModel):
    _name = 'hill.payment.register.wizard'
    _description = 'Hill Payment Register Wizard'

    case_id = fields.Many2one('hill.case', string='Case', required=True)
    amount = fields.Monetary(string='Amount', required=True, currency_field='currency_id')
    currency_id = fields.Many2one(related='case_id.currency_id', readonly=True)
    payment_date = fields.Date(string='Payment Date', required=True, default=fields.Date.today)
    payment_method = fields.Selection([
        ('bank', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
    ], string='Payment Method', required=True, default='bank')
    reference = fields.Char(string='Reference')
    notes = fields.Text(string='Notes')

    def action_confirm(self):
        self.ensure_one()
        self.env['hill.payment'].create({
            'case_id': self.case_id.id,
            'amount': self.amount,
            'payment_date': self.payment_date,
            'payment_method': self.payment_method,
            'reference': self.reference,
            'notes': self.notes,
        })
        self.case_id.write({
            'amount_total': self.amount,
            'payment_status': 'paid',
        })
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': _('Success'),
        #         'message': _('Payment registered successfully.'),
        #         'type': 'success',
        #         'sticky': False,
        #     },
        # }
