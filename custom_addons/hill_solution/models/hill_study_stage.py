from odoo import models, fields

class HillStudyStage(models.Model):
    _name = 'hill.study.stage'
    _description = 'Hill Study Stage'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    code = fields.Selection([
        ('to_process', 'To Process'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('to_modify', 'To Modify'),
        ('validated', 'Validated'),
    ], required=True, readonly=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(string='Folded in Kanban')

