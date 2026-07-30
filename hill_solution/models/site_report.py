import base64
from odoo import models, fields, api, _
from odoo.tools import html2plaintext
from odoo.exceptions import UserError


class SiteReport(models.Model):
    _name = 'site.report'
    _description = 'Site Visit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'visit_date desc, create_date desc'

    stage_id = fields.Many2one(
        'site.report.stage',
        string='Stage',
        required=True,
        default=lambda self: self.env.ref(
            'hill_solution.stage_tovisit', raise_if_not_found=False
        ).id,
        tracking=True,
        group_expand='_read_group_stage_ids',
    )
    stage_code = fields.Selection(
        related='stage_id.code',
        string='Stage Code',
        store=False,
    )
    name = fields.Char(string='Visit Title', required=True, tracking=True)
    case_id = fields.Many2one(
        'hill.case',
        string='Case',
        required=True,
        tracking=True,
        ondelete='cascade',
    )
    case_number = fields.Char(
        string='Case Number',
        related='case_id.case_number',
        store=True,
        tracking=True,
    )
    technician_name = fields.Many2one(
        'hr.employee',
        string='Technician',
        tracking=True,
    )
    technician_avatar = fields.Binary(
        related='technician_name.image_128',
        string='Technician Avatar',
        readonly=True,
    )

    client_type = fields.Selection(
        [('b2b', 'B2B'), ('b2c', 'B2C')],
        string='Client Type',
        tracking=True,
    )
    service_type = fields.Selection(
        [('both', 'Technical Visit + Study'),
         ('study', 'Study')],
        string='Service Type',
        tracking=True,
    )
    is_visit_required = fields.Boolean(string='Visit Required')

    company_name = fields.Char(string='Company Name', tracking=True)
    contact_firstname = fields.Char(string='Contact First Name')
    contact_lastname = fields.Char(string='Contact Last Name')
    b2b_phone = fields.Char(string='Phone Number')
    siret = fields.Char(string='SIRET Number', tracking=True)
    site_address = fields.Text(string='Site Address')

    beneficiary_firstname = fields.Char(string='Beneficiary First Name')
    beneficiary_lastname = fields.Char(string='Beneficiary Last Name')
    beneficiary_phone = fields.Char(string='Phone Number')
    beneficiary_status = fields.Selection(
        [('high_vulnerability', 'High-Vulnerability (Extreme Hardship)'),
         ('vulnerable', 'Vulnerable (Hardship)'),
         ('standard', 'Standard')],
        string='Beneficiary Status',
        tracking=True,
    )
    residential_address = fields.Text(string='Residential Address')

    visit_date = fields.Datetime(string='Visit Date', tracking=True)
    visit_duration = fields.Float(string='Duration (hours)', default=2.0)
    visit_notes = fields.Html(string='Visit Notes / Report')

    length = fields.Char(string='Length')
    breadth = fields.Char(string='Breadth')
    height = fields.Char(string='Height')
    area = fields.Char(string='Area')
    volume = fields.Char(string='Volume')
    temperature = fields.Char(string='Temperature')
    pressure = fields.Char(string='Pressure')

    document_ids = fields.One2many(
        'hill.site.document',
        'site_report_id',
        string='Documents',
    )
    photo_ids = fields.One2many(
        'hill.site.photo',
        'site_report_id',
        string='Photos',
    )

    # ── Computed ──────────────────────────────────────────────────────────────

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['site.report.stage'].search([], order=order or 'sequence')

    stage_name = fields.Char(
        compute='_compute_stage_name',
        string='Stage Name',
    )

    @api.depends('stage_id')
    def _compute_stage_name(self):
        for rec in self:
            rec.stage_name = rec.stage_id.name if rec.stage_id else ''

    is_to_visit = fields.Boolean(
        compute='_compute_is_to_visit',
    )

    @api.depends('stage_id')
    def _compute_is_to_visit(self):
        to_visit_stage = self.env.ref(
            'hill_solution.stage_tovisit', raise_if_not_found=False,
        )
        for rec in self:
            rec.is_to_visit = (
                rec.stage_id.id == to_visit_stage.id
                if to_visit_stage else False
            )

    is_requested = fields.Boolean(
        compute='_compute_is_requested',
    )

    @api.depends('stage_id')
    def _compute_is_requested(self):
        requested_stage = self.env.ref(
            'hill_solution.stage_requested', raise_if_not_found=False,
        )
        for rec in self:
            rec.is_requested = (
                rec.stage_id.id == requested_stage.id
                if requested_stage else False
            )

    is_rejected = fields.Boolean(
        compute='_compute_is_rejected',
    )

    @api.depends('stage_id')
    def _compute_is_rejected(self):
        rejected_stage = self.env.ref(
            'hill_solution.stage_rejected', raise_if_not_found=False,
        )
        for rec in self:
            rec.is_rejected = (
                rec.stage_id.id == rejected_stage.id
                if rejected_stage else False
            )

    # ── Actions ───────────────────────────────────────────────────────────────

    def action_propagate_site_fields(self):
        self.ensure_one()

        if not self.photo_ids:
            raise UserError(_('Please upload at least one photo before submitting.'))
        if not self.document_ids:
            raise UserError(_('Please upload at least one document before submitting.'))

        self.case_id.write({
            'length': self.length,
            'breadth': self.breadth,
            'height': self.height,
            'area': self.area,
            'volume': self.volume,
            'temperature': self.temperature,
            'pressure': self.pressure,
            'visit_notes': html2plaintext(self.visit_notes or ''),
        })

        requested_stage = self.env.ref(
            'hill_solution.stage_requested', raise_if_not_found=False,
        )
        if requested_stage:
            self.stage_id = requested_stage.id

        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': _('Success'),
        #         'message': _('Request Submitted successfully.'),
        #         'type': 'success',
        #         'sticky': False,
        #     }
        # }

    def action_generate_site_report(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Visit Report Preview'),
            'res_model': 'site.report.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_site_report_id': self.id,
            },
        }

    def action_save_site_report(self, pdf_data, filename):
        self.ensure_one()

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': pdf_data,
            'mimetype': 'application/pdf',
            'res_model': 'site.report',
            'res_id': self.id,
        })

        self.env['hill.site.document'].create({
            'site_report_id': self.id,
            'attachment_id': attachment.id,
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Report saved to documents.'),
                'type': 'success',
                'sticky': False,
            },
        }

    def action_revert_rejection(self):
        self.ensure_one()
        to_visit_stage = self.env.ref(
            'hill_solution.stage_tovisit', raise_if_not_found=False,
        )
        if to_visit_stage:
            self.stage_id = to_visit_stage.id
