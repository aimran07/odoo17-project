import base64
import subprocess
import tempfile
import os
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class HillCase(models.Model):
    _name = 'hill.case'
    _description = 'Hill Solution Cases'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'create_date desc'

    stage_id = fields.Many2one(
        'hill.case.stage',
        string='Stage',
        required=True,
        default=lambda self: self.env.ref('hill_solution.stage_new', raise_if_not_found=False).id,
        tracking=True,
        group_expand='_read_group_stage_ids'
    )
    stage_code = fields.Selection(
        related='stage_id.code',
        string='Stage Code',
        store=False,
    )
    name = fields.Char(
        string='Case Title',
        # required=True,
        tracking=True,
        help="Title of the case"
    )
    case_number = fields.Char(
        string='Case Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True,
        help="Unique case number generated automatically"
    )
    client_type = fields.Selection(
        [('b2b', 'B2B'), ('b2c', 'B2C')],
        string='Client Type', required=True, tracking=True,
    )
    service_type = fields.Selection(
        [('both', 'Technical Visit + Study'),
         ('study', 'Study')],
        string='Service Type',
        # required=True,
        tracking=True,
    )
    prestation_type = fields.Selection(
        [('otg', 'Obligation to Give'),
         ('otd', 'Obligation to Do'),
         ('ontd', 'Obligation Not to Do')],
        string='Prestation Type',
        tracking=True,
    )
    is_visit_required = fields.Boolean(
        string='Visit Required',
        compute='_compute_is_visit_required',
        store=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        tracking=True,
    )
    date_deadline = fields.Date(string='Deadline', tracking=True)
    agent_name = fields.Many2one(
        'hr.employee',
        string="Agent Name",
    )
    agent_avatar = fields.Binary(
        related='agent_name.image_128',
        string='Agent Avatar',
        readonly=True,
    )
    technician_name = fields.Many2one(
        'hr.employee',
        string="Technician Name",
        # groups="crm.group_crm_manager"
    )
    technician_avatar = fields.Binary(
        related='technician_name.image_128',
        string='Technician Avatar',
        readonly=True,
    )
    appointment_status = fields.Selection(
           [('to_contact', 'To Be Contacted'),
            ('scheduled', 'Appointment Scheduled'),
            ('npj', 'Client Unreachable (NPJ)'),
            ('to_recontact', 'To Be Re-contacted'),
            ('confirmed', 'Appointment Confirmed')],
        string='Appointment Status', default='to_contact', tracking=True,
    )
    invoice_id = fields.Many2one(
        'hill.invoice',
        string='Invoice',
        readonly=True,
        copy=False,
    )
    is_validated = fields.Boolean(
        string='Validated',
        default=False,
        tracking=True,
    )
    validated_badge = fields.Char(
        compute="_compute_validated_badge",
        store=False
    )

    @api.depends("is_validated")
    def _compute_validated_badge(self):
        for rec in self:
            rec.validated_badge = _("VALIDATED") if rec.is_validated else False



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
        string='Beneficiary Status', tracking=True,
    )
    residential_address = fields.Text(string='Residential Address')

    visit_date = fields.Date(string='Visit Date', tracking=True)
    visit_duration = fields.Float(string='Duration (hours)', default=2.0)
    visit_notes = fields.Text(string='Visit Notes / Report')

    study_nature = fields.Selection(
        [('destratification', 'Destratification Fans Sizing'),
         ('led', 'LED Lighting Sizing'),
         ('other', 'Other')],
        string='Study Nature',
    )
    study_status = fields.Selection(
        [('pending', 'Pending'),
         ('in_progress', 'In Progress'),
         ('completed', 'Completed'),
         ('requires_modification', 'Requires Modification'),
         ('validated', 'Validated')],
        string='Study Status', default='pending', tracking=True,
    )
    study_notes = fields.Html(string='Study Notes')
    study_data = fields.Text(string='Study Input Data')

    amount_total = fields.Monetary(
        string='Amount', currency_field='currency_id',
    )
    payment_status = fields.Selection(
        [('unpaid', 'Unpaid'),
         ('awaiting', 'Awaiting Payment'),
         ('paid', 'Paid')],
        string='Payment Status', default='unpaid', tracking=True,
    )
    invoice_status = fields.Selection(
        [('not_invoiced', 'Not Invoiced'),
         ('invoiced', 'Invoiced'),
         ('partially_invoiced', 'Partially Invoiced')],
        string='Invoice Status', default='not_invoiced', tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    payment_ids = fields.One2many(
        'hill.payment', 'case_id', string='Payments',
    )
    invoice_attachment_id = fields.Many2one(
        'ir.attachment', string='Invoice PDF', readonly=True,
    )

    length = fields.Char(string='Length', readonly=True)
    breadth = fields.Char(string='Breadth', readonly=True)
    height = fields.Char(string='Height', readonly=True)
    area = fields.Char(string='Area', readonly=True)
    volume = fields.Char(string='Volume', readonly=True)
    temperature = fields.Char(string='Temperature', readonly=True)
    pressure = fields.Char(string='Pressure', readonly=True)

    site_report_ids = fields.One2many(
        'site.report',
        'case_id',
        string='Site Reports',
    )
    document_ids_direct = fields.One2many(
        'hill.site.document',
        'case_id',
        string='Direct Documents',
    )
    study_ids = fields.One2many(
        'hill.study',
        'case_id',
        string='Studies',
    )
    document_ids = fields.Many2many(
        'hill.site.document',
        compute='_compute_case_documents',
        string='Documents',
    )
    photo_ids = fields.Many2many(
        'hill.site.photo',
        compute='_compute_case_photos',
        string='Photos',
    )

    @api.depends('site_report_ids.document_ids', 'document_ids_direct')
    def _compute_case_documents(self):
        for rec in self:
            rec.document_ids = rec.site_report_ids.mapped('document_ids') | rec.document_ids_direct

    @api.depends('site_report_ids.photo_ids')
    def _compute_case_photos(self):
        for rec in self:
            rec.photo_ids = rec.site_report_ids.mapped('photo_ids')

    @api.model
    def create(self, vals):
        if vals.get('case_number', _('New')) == _('New'):
            vals['case_number'] = self.env['ir.sequence'].next_by_code('hill.case') or _('New')
        return super(HillCase, self).create(vals)

    @api.depends('service_type', 'study_nature')
    def _compute_is_visit_required(self):
        for rec in self:
            if rec.service_type == 'study' and rec.study_nature in ('destratification', 'led'):
                rec.is_visit_required = False
            else:
                rec.is_visit_required = rec.service_type in ('technical_visit', 'both')

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['hill.case.stage'].search([], order='sequence')

    def action_create_visit_from_case(self):
        self.ensure_one()

        # if not self.technician_name:
        #     raise ValidationError(_("Please select a Technician before creating the site visit."))

        if not self.technician_name:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Validation Error'),
                    'message': _('Please select a Technician before creating the site visit.'),
                    'type': 'danger',   # or 'warning'
                    'sticky': False,
                }
            }

        if self.site_report_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Warning'),
                    'message': _('A site visit already exists for this case.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }

        default_stage = self.env.ref('hill_solution.stage_tovisit', raise_if_not_found=False)
        visit_values = {
            'case_id': self.id,
            # 'name': _('%s - %s') % (self.case_number or 'Case', self.name or 'Site Visit'),
            'name': self.name or _('Site Visit'),
            'technician_name': self.technician_name.id if self.technician_name else False,
            'stage_id': default_stage.id if default_stage else False,
            'client_type': self.client_type,
            'service_type': self.service_type,
            'is_visit_required': self.is_visit_required,
            'company_name': self.company_name,
            'contact_firstname': self.contact_firstname,
            'contact_lastname': self.contact_lastname,
            'b2b_phone': self.b2b_phone,
            'siret': self.siret,
            'site_address': self.site_address or self.residential_address,
            'beneficiary_firstname': self.beneficiary_firstname,
            'beneficiary_lastname': self.beneficiary_lastname,
            'beneficiary_phone': self.beneficiary_phone,
            'beneficiary_status': self.beneficiary_status,
            'residential_address': self.residential_address,
            'visit_date': self.visit_date,
            'visit_duration': self.visit_duration,
        }
        visit = self.env['site.report'].create(visit_values)

        visit_stage = self.env.ref(
            'hill_solution.stage_visit',
            raise_if_not_found=False,
        )
        if visit_stage:
            self.stage_id = visit_stage.id

        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': _('Success'),
        #         'message': _('Site visit created successfully.'),
        #         'type': 'success',
        #         'sticky': False,
        #     }
        # }

    def action_validate_case(self):
        for rec in self:
            if rec.is_validated:
                raise UserError(_("This case has already been validated."))

            rec.is_validated = True

        for rec in self:
            if not rec.agent_name and self.env.user.employee_id:
                rec.agent_name = self.env.user.employee_id

        appointment_stage = self.env.ref(
            'hill_solution.stage_appointment', raise_if_not_found=False,
        )
        if appointment_stage:
            self.stage_id = appointment_stage.id

        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': _('Success'),
        #         'message': _('Case Validated.'),
        #         'type': 'success',
        #         'sticky': False,
        #     }
        # }

    def action_validate_study(self):
        self.ensure_one()

        # Get related study
        study = self.study_ids[:1]

        if not study:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('No study found for this dossier.'),
                    'type': 'danger',
                    'sticky': False,
                }
            }

        # Move study to Validated
        validated_study_stage = self.env.ref(
            'hill_solution.stage_validated',
            raise_if_not_found=False,
        )

        if validated_study_stage:
            study.write({
                'stage_id': validated_study_stage.id,
                'study_status': 'validated',
            })

        # Update case study status
        self.write({
            'study_status': 'validated',
        })

        # Move case to Invoice/Payment stage
        invoice_stage = self.env.ref(
            'hill_solution.stage_invoice_payment',
            raise_if_not_found=False,
        )

        if invoice_stage:
            self.write({
                'stage_id': invoice_stage.id,
            })

        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': _('Success'),
        #         'message': _('Study validated successfully.'),
        #         'type': 'success',
        #         'sticky': False,
        #     }
        # }

    def action_request_modification(self):
        self.ensure_one()
        study = self.study_ids[:1]
        if not study:
            return
        to_modify_stage = self.env.ref(
            'hill_solution.stage_to_modify',
            raise_if_not_found=False,
        )
        if to_modify_stage:
            study.write({
                'stage_id': to_modify_stage.id,
                'study_status': 'requires_modification',
            })
        self.write({'study_status': 'requires_modification'})

    # def write(self, vals):
    #     if 'stage_id' in vals:
    #         new_stage = self.env['hill.case.stage'].browse(vals['stage_id'])
    #         for rec in self:
    #             if new_stage.sequence < rec.stage_id.sequence:
    #                 raise UserError(
    #                     _('You cannot move it to a previous stage.')
    #                 )
    #     return super().write(vals)

    def action_approve_visit_details(self):
        self.ensure_one()

        # 1. Move site.report to approved stage
        requested_stage = self.env.ref('hill_solution.stage_requested', raise_if_not_found=False)
        approved_stage = self.env.ref('hill_solution.stage_approved', raise_if_not_found=False)

        if requested_stage and approved_stage:
            pending_reports = self.site_report_ids.filtered(
                lambda r: r.stage_id.id == requested_stage.id
            )
            pending_reports.write({'stage_id': approved_stage.id})

        # 2. Move hill.case to Visit stage
        visit_stage = self.env.ref('hill_solution.stage_visit', raise_if_not_found=False)
        if visit_stage:
            self.stage_id = visit_stage.id

        # 3. Success notification
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': _('Approved'),
        #         'message': _('Visit details approved successfully.'),
        #         'type': 'success',
        #         'sticky': False,
        #     }
        # }
    def action_reject_visit_details(self):
        self.ensure_one()

        # 1. Move site.report to approved stage
        requested_stage = self.env.ref('hill_solution.stage_requested', raise_if_not_found=False)
        rejected_stage = self.env.ref('hill_solution.stage_rejected', raise_if_not_found=False)

        if requested_stage and rejected_stage:
            pending_reports = self.site_report_ids.filtered(
                lambda r: r.stage_id.id == requested_stage.id
            )
            pending_reports.write({'stage_id': rejected_stage.id})

        # 2. Move hill.case to Visit stage
        visit_stage = self.env.ref('hill_solution.stage_visit', raise_if_not_found=False)
        if visit_stage:
            self.stage_id = visit_stage.id

        # 3. Success notification
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': _('Rejected'),
        #         'message': _('Visit details rejected.'),
        #         'type': 'danger',
        #         'sticky': False,
        #     }
        # }

    def action_register_payment(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Register Payment'),
            'res_model': 'hill.payment.register.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_case_id': self.id,
                'default_amount': self.amount_total,
            },
        }

    def action_create_invoice(self):
        self.ensure_one()
        return self.partner_id.with_context(
            default_case_id=self.id
        ).action_open_invoice_wizard()

    def _generate_invoice_pdf(self):
        self.ensure_one()
        partner = self.partner_id.name if self.partner_id else ''
        payment_info = ''
        if self.payment_ids:
            lines = []
            for p in self.payment_ids:
                lines.append(
                    '<tr><td>%s</td><td>%s</td><td>%.2f</td><td>%s</td></tr>' % (
                        p.payment_date or '',
                        dict(p._fields['payment_method'].selection).get(p.payment_method, p.payment_method or ''),
                        p.amount or 0.0,
                        p.reference or '',
                    )
                )
            payment_info = '''
            <div class="section">
                <h2>%s</h2>
                <table>
                    <tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>
                    %s
                </table>
            </div>''' % (_('Payments'), _('Date'), _('Method'), _('Amount'), _('Reference'), '\n'.join(lines))

        html = '''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
    body { font-family: Arial, sans-serif; font-size: 11pt; color: #333; margin: 0; padding: 0; }
    .header { text-align: center; border-bottom: 2px solid #2E86C1; padding-bottom: 10px; margin-bottom: 20px; }
    .header h1 { color: #2E86C1; font-size: 20pt; margin: 0; }
    .header p { color: #666; font-size: 10pt; margin: 5px 0 0; }
    .section { margin-bottom: 20px; }
    .section h2 { font-size: 13pt; color: #2E86C1; border-bottom: 1px solid #ddd; padding-bottom: 4px; margin: 0 0 10px; }
    table { width: 100%%; border-collapse: collapse; }
    table td, table th { padding: 4px 8px; vertical-align: top; text-align: left; }
    table th { background: #f0f0f0; font-weight: bold; }
    .label { font-weight: bold; color: #555; width: 35%%; }
    .value { color: #333; }
    .total { font-weight: bold; font-size: 13pt; text-align: right; margin-top: 20px; border-top: 2px solid #2E86C1; padding-top: 10px; }
</style>
</head>
<body>
    <div class="header">
        <h1>%(invoice_label)s</h1>
        <p>%(case_number)s</p>
    </div>

    <div class="section">
        <h2>%(invoice_info_label)s</h2>
        <table>
            <tr><td class="label">%(invoice_number_label)s</td><td class="value">%(invoice_number)s</td></tr>
            <tr><td class="label">%(invoice_date_label)s</td><td class="value">%(invoice_date)s</td></tr>
            <tr><td class="label">%(case_title_label)s</td><td class="value">%(case_title)s</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>%(bill_to_label)s</h2>
        <table>
            <tr><td class="label">%(client_label)s</td><td class="value">%(partner)s</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>%(invoice_lines_label)s</h2>
        <table>
            <tr><th>%(description_label)s</th><th>%(qty_label)s</th><th>%(price_label)s</th><th>%(total_label)s</th></tr>
            <tr><td>%(description)s</td><td>1</td><td>%(amount)s</td><td>%(amount)s</td></tr>
        </table>
    </div>

    <div class="total">
        %(total_label)s: %(amount)s %(currency)s
    </div>

    %(payment_info)s
</body>
</html>
''' % {
            'case_number': self.case_number or '',
            'invoice_label': _('INVOICE'),
            'invoice_info_label': _('Invoice Information'),
            'invoice_number_label': _('Invoice Number'),
            'invoice_number': 'INV-%s' % (self.case_number or str(self.id)),
            'invoice_date_label': _('Invoice Date'),
            'invoice_date': str(fields.Date.today()),
            'case_title_label': _('Case Title'),
            'case_title': self.name or '',
            'bill_to_label': _('Bill To'),
            'client_label': _('Client'),
            'invoice_lines_label': _('Invoice Lines'),
            'description_label': _('Description'),
            'qty_label': _('Qty'),
            'price_label': _('Price'),
            'total_label': _('Total'),
            'partner': partner,
            'description': self.name or _('Service'),
            'amount': '%.2f' % (self.amount_total or 0.0),
            'currency': self.currency_id.symbol or '',
            'payment_info': payment_info,
        }

        with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as f:
            f.write(html)
            html_path = f.name
        pdf_path = html_path + '.pdf'
        try:
            subprocess.run([
                'wkhtmltopdf',
                '--page-size', 'A4',
                '--margin-top', '15mm',
                '--margin-bottom', '15mm',
                '--margin-left', '15mm',
                '--margin-right', '15mm',
                '--enable-local-file-access',
                html_path, pdf_path,
            ], check=True, capture_output=True)
            with open(pdf_path, 'rb') as f:
                return f.read()
        finally:
            os.unlink(html_path)
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)

    can_create_study = fields.Boolean(
        compute='_compute_can_create_study',
        string='Can Create Study',
    )

    @api.depends('stage_id', 'site_report_ids.stage_id')
    def _compute_can_create_study(self):
        visit_stage = self.env.ref('hill_solution.stage_visit', raise_if_not_found=False)
        approved_stage = self.env.ref('hill_solution.stage_approved', raise_if_not_found=False)
        for rec in self:
            rec.can_create_study = (
                visit_stage and approved_stage and
                rec.stage_id.id == visit_stage.id and
                rec.site_report_ids and
                all(r.stage_id.id == approved_stage.id for r in rec.site_report_ids)
            )

    def action_create_study(self):
        self.ensure_one()
        study_stage = self.env.ref('hill_solution.stage_to_process', raise_if_not_found=False)
        approved_report = self.site_report_ids.filtered(
            lambda r: r.stage_id.id == self.env.ref('hill_solution.stage_approved').id
        )[-1] if self.site_report_ids else False

        if not approved_report:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('No approved visit found.'),
                    'type': 'danger',
                    'sticky': False,
                }
            }

        study_values = {
            'case_id': self.id,
            'case_number': self.case_number,
            'name': self.name or _('Study'),
            'stage_id': study_stage.id if study_stage else False,
            'site_report_id': approved_report.id,
            'client_type': self.client_type,
            'company_name': self.company_name,
            'contact_firstname': self.contact_firstname,
            'contact_lastname': self.contact_lastname,
            'b2b_phone': self.b2b_phone,
            'siret': self.siret,
            'site_address': self.site_address or self.residential_address,
            'beneficiary_firstname': self.beneficiary_firstname,
            'beneficiary_lastname': self.beneficiary_lastname,
            'beneficiary_phone': self.beneficiary_phone,
            'beneficiary_status': self.beneficiary_status,
            'residential_address': self.residential_address,
            'visit_date': approved_report.visit_date,
            'visit_duration': approved_report.visit_duration,
            'visit_notes': approved_report.visit_notes,
            'length': self.length,
            'breadth': self.breadth,
            'height': self.height,
            'area': self.area,
            'volume': self.volume,
            'temperature': self.temperature,
            'pressure': self.pressure,
            'study_nature': self.study_nature,
            'study_notes': self.study_notes,
            'study_data': self.study_data,
        }
        self.env['hill.study'].create(study_values)

        study_stage_case = self.env.ref('hill_solution.stage_study', raise_if_not_found=False)
        if study_stage_case:
            self.stage_id = study_stage_case.id

        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': _('Success'),
        #         'message': _('Study created successfully.'),
        #         'type': 'success',
        #         'sticky': False,
        #     }
        # }

    has_pending_approval = fields.Boolean(
        compute='_compute_has_pending_approval',
        string='Has Pending Approval',
    )

    @api.depends('site_report_ids.stage_id')
    def _compute_has_pending_approval(self):
        requested_stage = self.env.ref(
            'hill_solution.stage_requested',
            raise_if_not_found=False,
        )
        for rec in self:
            if requested_stage:
                rec.has_pending_approval = any(
                    r.stage_id.id == requested_stage.id
                    for r in rec.site_report_ids
                )
            else:
                rec.has_pending_approval = False

    is_visit = fields.Boolean(
        compute='_compute_is_visit',
    )

    @api.depends('stage_id')
    def _compute_is_visit(self):
        visit_stage = self.env.ref(
            'hill_solution.stage_visit',
            raise_if_not_found=False,
        )
        for rec in self:
            rec.is_visit = (
                rec.stage_id.id == visit_stage.id if visit_stage else False
            )

    is_new_case = fields.Boolean(
        compute='_compute_is_new_case',
    )

    @api.depends('stage_id')
    def _compute_is_new_case(self):
        new_stage = self.env.ref(
            'hill_solution.stage_new',
            raise_if_not_found=False,
        )
        for rec in self:
            rec.is_new_case = (
                rec.stage_id.id == new_stage.id if new_stage else False
            )

    has_site_visit = fields.Boolean(
        compute="_compute_has_site_visit",
        string="Has Site Visit",
    )

    @api.depends('site_report_ids')
    def _compute_has_site_visit(self):
        for rec in self:
            rec.has_site_visit = bool(rec.site_report_ids)

    # is_to_be_contacted = fields.Boolean(
    #     compute='_compute_is_to_be_contacted',
    # )

    is_appointment = fields.Boolean(
        compute = '_compute_is_appointment'
    )

    @api.depends('stage_id')
    def _compute_is_appointment(self):
        appointment_stage = self.env.ref(
            'hill_solution.stage_appointment',
            raise_if_not_found=False,
        )
        for rec in self:
            rec.is_appointment = (
                rec.stage_id.id == appointment_stage.id if appointment_stage else False
            )

    is_study = fields.Boolean(
        compute = '_compute_is_study'
    )

    @api.depends('stage_id')
    def _compute_is_study(self):
        study_stage = self.env.ref(
            'hill_solution.stage_study',
            raise_if_not_found=False,
        )
        for rec in self:
            rec.is_study = (
                rec.stage_id.id == study_stage.id if study_stage else False
            )

    is_study_status_completed = fields.Boolean(
        compute='_compute_is_study_status_completed',
    )

    @api.depends('study_status')
    def _compute_is_study_status_completed(self):
        for rec in self:
            rec.is_study_status_completed = (rec.study_status == 'completed')

    is_study_to_modify = fields.Boolean(
        compute='_compute_is_study_to_modify',
    )

    @api.depends('study_status')
    def _compute_is_study_to_modify(self):
        for rec in self:
            rec.is_study_to_modify = (rec.study_status == 'requires_modification')

    is_invoice_payment = fields.Boolean(
        compute = '_compute_is_invoice_payment'
    )

    @api.depends('stage_id')
    def _compute_is_invoice_payment(self):
        invoice_payment_stage = self.env.ref(
            'hill_solution.stage_invoice_payment',
            raise_if_not_found=False,
        )
        for rec in self:
            rec.is_invoice_payment = (
                rec.stage_id.id == invoice_payment_stage.id if invoice_payment_stage else False
            )

    is_payment_status_paid = fields.Boolean(
        compute='_compute_is_payment_status_paid',
    )

    @api.depends('payment_status')
    def _compute_is_payment_status_paid(self):
        for rec in self:
            rec.is_payment_status_paid = (rec.payment_status == 'paid')

    site_report_stage = fields.Char(
        compute='_compute_site_report_stage',
        string='Visit Stage',
    )

    @api.depends('site_report_ids.stage_id')
    def _compute_site_report_stage(self):
        for rec in self:
            if rec.site_report_ids:
                latest = rec.site_report_ids.sorted('create_date', reverse=True)[0]
                rec.site_report_stage = latest.stage_id.name
            else:
                rec.site_report_stage = False

    user_is_manager = fields.Boolean(
        compute='_compute_user_is_manager',
    )

    def _compute_user_is_manager(self):
        is_manager = self.env.user.has_group(
            'hill_solution.hill_case_manager'
        )
        for rec in self:
            rec.user_is_manager = is_manager

    @api.model
    def get_busy_dates(self, technician_id):

        if not technician_id:
            return []

        cases = self.search([
            ("technician_name", "=", technician_id),
            ("visit_date", "!=", False),
        ])

        return [
            case.visit_date.strftime("%Y-%m-%d")
            for case in cases
        ]

    # @api.depends('stage_id')
    # def _compute_is_to_be_contacted(self):
    #     to_be_contacted_stage = self.env.ref(
    #         'hill_solution.stage_tobecontacted',
    #         raise_if_not_found=False,
    #     )
    #     for rec in self:
    #         rec.is_to_be_contacted = (
    #             rec.stage_id.id == to_be_contacted_stage.id if to_be_contacted_stage else False
    #         )

    # def _default_stage_id(self):
    #     return self.env.ref('hill_solution.stage_new', raise_if_not_found=False)

    # def _expand_stages(self, states, domain, order):
    #     return ['new', 'technician_assigned', 'visit_completed', 'visit_cancelled',]


    # def action_assign_technician(self):
    #     self.write({'stage': 'assigned'})

    # def action_complete(self):
    #     self.write({'stage': 'completed'})

    # def action_cancel(self):
    #     self.write({'stage': 'cancelled'})

    # def action_reset_to_new(self):
    #     self.write({'stage': 'new'})
