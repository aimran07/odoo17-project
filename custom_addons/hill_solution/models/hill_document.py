from odoo import api, fields, models, _
import base64

class HillDocument(models.Model):
    _name = 'hill.document'
    _description = 'E-Sign Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    doc_type = fields.Selection(
        [('visit', 'Visit Report'),
         ('study', 'Study Report')],
        string='Document Type',
        required=True,
        tracking=True,
    )
    site_report_id = fields.Many2one(
        'site.report',
        string='Site Report',
        ondelete='cascade',
    )
    study_id = fields.Many2one(
        'hill.study',
        string='Study',
        ondelete='cascade',
    )
    case_id = fields.Many2one(
        'hill.case',
        string='Case',
        ondelete='cascade',  
    )
    case_number = fields.Char(
        string='Case Number',
        related='case_id.case_number',
        store=True,
        tracking=True,
    )
    name = fields.Char(
        string='Document Title',
        compute='_compute_name',
        store=True,
        tracking=True,
    )
    state = fields.Selection(
        [('unsigned', 'Unsigned'),
         ('signed', 'Signed')],
        string='Status',
        default='unsigned',
        tracking=True,
    )
    original_attachment_id = fields.Many2one(
        'ir.attachment',
        string='Original Document',
        readonly=True,
    )
    signature = fields.Binary(
        string='Signature',
    )
    signature_type = fields.Selection(
        [('drawn', 'Drawn'),
         ('typed', 'Typed'),
         ('uploaded', 'Uploaded')],
        string='Signature Type',
        readonly=True,
    )
    signature_name = fields.Char(
        string='Signed By Name',
        readonly=True,
    )
    signed_by = fields.Many2one(
        'res.users',
        string='Signed By',
        readonly=True,
    )
    sign_date = fields.Datetime(
        string='Signed On',
        readonly=True,
    )
    signed_attachment_id = fields.Many2one(
        'ir.attachment',
        string='Signed Document',
        readonly=True,
    )

    associated_document_ids = fields.Many2many(
        'hill.site.document',
        compute='_compute_associated_documents',
        string='Associated Documents',
    )

    @api.depends('doc_type', 'site_report_id.document_ids', 'study_id.document_ids',
                 'original_attachment_id')
    def _compute_associated_documents(self):
        for rec in self:
            if rec.doc_type == 'visit':
                docs = rec.site_report_id.document_ids
            elif rec.doc_type == 'study':
                docs = rec.study_id.document_ids
            else:
                docs = self.env['hill.site.document']
            rec.associated_document_ids = docs.filtered(
                lambda d: d.attachment_id == rec.original_attachment_id
            )

    @api.depends('doc_type', 'site_report_id.name', 'study_id.name')
    def _compute_name(self):
        for rec in self:
            if rec.doc_type == 'visit' and rec.site_report_id:
                rec.name = rec.site_report_id.name
            elif rec.doc_type == 'study' and rec.study_id:
                rec.name = rec.study_id.name
            else:
                rec.name = False

    def action_open_sign_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sign Document'),
            'res_model': 'hill.sign.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_document_id': self.id,
            },
        }

    def action_generate_signed_pdf(self):
        self.ensure_one()

        report = None
        if self.doc_type == 'visit':
            report = self.site_report_id
        elif self.doc_type == 'study':
            report = self.study_id

        if not report:
            return False

        if self.doc_type == 'visit':
            wizard = self.env['site.report.wizard'].create({
                'site_report_id': report.id,
            })
            pdf_data = wizard._generate_pdf(
                report,
                signature_image=self.signature,
                signature_name=self.signature_name,
            )
        else:
            wizard = self.env['study.report.wizard'].create({
                'study_id': report.id,
            })
            pdf_data = wizard._generate_pdf(
                report,
                signature_image=self.signature,
                signature_name=self.signature_name,
            )

        attachment = self.env['ir.attachment'].create({
            'name': 'signed_%s_%s.pdf' % (
                'visit' if self.doc_type == 'visit' else 'study',
                report.id,
            ),
            'type': 'binary',
            'datas': base64.b64encode(pdf_data),
            'mimetype': 'application/pdf',
            'res_model': 'hill.document',
            'res_id': self.id,
        })
        self.signed_attachment_id = attachment.id

        return attachment

    def action_view_signed_pdf(self):
        self.ensure_one()
        if not self.signed_attachment_id:
            return False
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=false' % self.signed_attachment_id.id,
            'target': 'new',
        }
