from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HillSignWizard(models.TransientModel):
    _name = 'hill.sign.wizard'
    _description = 'Sign Document Wizard'

    document_id = fields.Many2one(
        'hill.document',
        string='Document',
        required=True,
        readonly=True,
    )
    method = fields.Selection(
        [('draw', 'Draw'),
         ('type', 'Type Name'),
         ('upload', 'Upload')],
        string='Signing Method',
        default='draw',
        required=True,
    )
    draw_signature = fields.Binary(string='Draw Signature')
    typed_name = fields.Char(string='Typed Name')
    suggested_signature_id = fields.Many2one(
        'hill.signature',
        string='Suggested Signature',
    )
    uploaded_signature = fields.Binary(string='Uploaded Signature')
    uploaded_filename = fields.Char(string='Uploaded Filename')

    def _get_signature_data(self):
        self.ensure_one()

        if self.method == 'draw':
            if not self.draw_signature:
                raise UserError(_('Please draw your signature first.'))
            return self.draw_signature, 'drawn', self._default_signature_name()

        if self.method == 'type':
            if not self.typed_name:
                raise UserError(_('Please type a name to sign with.'))
            if not self.suggested_signature_id:
                raise UserError(_('Please select a suggested signature image.'))
            return self.suggested_signature_id.image, 'typed', self.typed_name

        if self.method == 'upload':
            if not self.uploaded_signature:
                raise UserError(_('Please upload a signature image first.'))
            return self.uploaded_signature, 'uploaded', self._default_signature_name()

        raise UserError(_('Please choose a signing method.'))

    def _default_signature_name(self):
        user = self.env.user
        if user.name:
            return user.name
        return user.login

    def action_confirm(self):
        self.ensure_one()

        signature, signature_type, signature_name = self._get_signature_data()

        self.document_id.write({
            'signature': signature,
            'signature_type': signature_type,
            'signature_name': signature_name,
            'signed_by': self.env.user.id,
            'sign_date': fields.Datetime.now(),
        })

        signed_attachment = self.document_id.action_generate_signed_pdf()
        if signed_attachment:
            self.document_id.write({
                'signed_attachment_id': signed_attachment.id,
                'state': 'signed',
            })
            self.document_id.message_post(
                body=_('Document signed by %s on %s.') % (
                    signature_name,
                    fields.Datetime.now().strftime('%Y-%m-%d %H:%M'),
                ),
            )
        else:
            self.document_id.message_post(
                body=_('Document marked as signed by %s (no PDF generated).') % signature_name,
            )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Document signed successfully.'),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    @api.onchange('typed_name')
    def _onchange_typed_name(self):
        domain = []
        if self.typed_name:
            domain = [('name', 'ilike', self.typed_name)]
        return {
            'domain': {
                'suggested_signature_id': domain,
            },
        }
