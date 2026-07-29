from odoo import models, fields, api


class SiteReportStage(models.Model):
    _name = 'site.report.stage'
    _description = 'Site Visit Stage'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    code = fields.Selection([
        ('to_visit', 'To visit'),
        ('requested_for_approval', 'Requested For Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], required=True, readonly=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(string='Folded in Kanban')

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['site.report.stage'].search([], order=order or 'sequence')
