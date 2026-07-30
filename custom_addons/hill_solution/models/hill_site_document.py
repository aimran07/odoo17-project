from odoo import models, fields, api, _

class HillSiteDocument(models.Model):
    _name = 'hill.site.document'
    _description = 'Site Visit Document'
    _order = 'uploaded_at desc'

    site_report_id = fields.Many2one(
        'site.report',
        string='Site Report',
        ondelete='cascade',
    )
    case_id = fields.Many2one(
        'hill.case',
        string='Case',
        ondelete='cascade',
    )
    attachment_id = fields.Many2one(
        'ir.attachment',
        string='File',
        required=True,
        ondelete='cascade',
    )
    uploaded_at = fields.Datetime(
        string='Uploaded At',
        default=fields.Datetime.now,
        readonly=True,
    )

    name = fields.Char(
        related='attachment_id.name',
        readonly=True,
        store=True,
    )
    mimetype = fields.Char(
        related='attachment_id.mimetype',
        readonly=True,
        store=True,
    )
    file_size = fields.Integer(
        related='attachment_id.file_size',
        readonly=True,
        store=True,
    )

    display_name = fields.Char(
        compute='_compute_display_name',
        string='Display Name',
    )

    @api.depends('attachment_id.name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.name or _('Document')
