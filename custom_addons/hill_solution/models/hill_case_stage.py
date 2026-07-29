from odoo import models, fields

class HillCaseStage(models.Model):
    _name = 'hill.case.stage'
    _description = 'Hill Case Stage'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    code = fields.Selection([
        ('new', 'New'),
        ('appointment', 'Appointment'),
        ('visit', 'Visit'),
        ('study', 'Study'),
        ('invoice_payment', 'Invoice/Payment'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], required=True, readonly=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(string='Folded in Kanban')
