from odoo import models, fields


class HillSitePhoto(models.Model):
    _name = 'hill.site.photo'
    _description = 'Site Visit Photo'
    _order = 'uploaded_at desc'

    site_report_id = fields.Many2one(
        'site.report',
        string='Site Report',
        required=True,
        ondelete='cascade',
    )
    attachment_id = fields.Many2one(
        'ir.attachment',
        string='Photo',
        required=True,
        ondelete='cascade',
    )
    uploaded_at = fields.Datetime(
        string='Uploaded At',
        default=fields.Datetime.now,
        readonly=True,
    )

    # Helpers
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
