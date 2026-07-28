from odoo import models, fields, api, _

class HillStudy(models.Model):
    _name = 'hill.study'
    _description = 'Hill Study'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Study Title', required=True, tracking=True)
    case_number = fields.Char(string='Case Number', required=True, copy=False, tracking=True)
    case_id = fields.Many2one('hill.case', string='Case', required=True, ondelete='cascade')
    site_report_id = fields.Many2one('site.report', string='Site Report', required=True, ondelete='cascade')

    stage_id = fields.Many2one(
        'hill.study.stage',
        string='Stage',
        required=True,
        default=lambda self: self.env.ref('hill_solution.stage_to_process', raise_if_not_found=False).id,
        tracking=True,
        group_expand='_read_group_stage_ids',
    )

    client_type = fields.Selection(
        [('b2b', 'B2B'), ('b2c', 'B2C')],
        string='Client Type',
        tracking=True,
    )

    is_to_process = fields.Boolean(
        compute='_compute_is_to_process',
    )

    @api.depends('stage_id')
    def _compute_is_to_process(self):
        to_process_stage = self.env.ref(
            'hill_solution.stage_to_process',
            raise_if_not_found=False,
        )
        for rec in self:
            rec.is_to_process = (
                rec.stage_id.id == to_process_stage.id if to_process_stage else False
            )

    is_in_progress = fields.Boolean(
        compute='_compute_is_in_progress',
    )

    @api.depends('stage_id')
    def _compute_is_in_progress(self):
        in_progress_stage = self.env.ref(
            'hill_solution.stage_in_progress',
            raise_if_not_found=False,
        )
        for rec in self:
            rec.is_in_progress = (
                rec.stage_id.id == in_progress_stage.id if in_progress_stage else False
            )

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
    visit_duration = fields.Float(string='Duration (hours)')
    visit_notes = fields.Text(string='Visit Notes / Report')

    length = fields.Char(string='Length')
    breadth = fields.Char(string='Breadth')
    height = fields.Char(string='Height')
    area = fields.Char(string='Area')
    volume = fields.Char(string='Volume')
    temperature = fields.Char(string='Temperature')
    pressure = fields.Char(string='Pressure')

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
        string='Study Status',
        default='pending',
        tracking=True,
    )
    study_notes = fields.Html(string='Study Notes')
    study_data = fields.Text(string='Study Input Data')

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['hill.study.stage'].search([], order='sequence')

    def action_start_study(self):
        in_progress_stage = self.env.ref(
            'hill_solution.stage_in_progress',
            raise_if_not_found=False,
        )
        self.study_status = 'in_progress'

        if in_progress_stage:
            self.stage_id = in_progress_stage.id

        # Write back to parent case
        if self.case_id:
            self.case_id.write({
                'study_status': 'in_progress',
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Study Started.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_study_complete(self):
        completed_stage = self.env.ref(
            'hill_solution.stage_completed',
            raise_if_not_found=False,
        )
        self.study_status = 'completed'

        if completed_stage:
            self.stage_id = completed_stage.id

        # Write back to parent case
        if self.case_id:
            self.case_id.write({
                'study_status': 'completed',
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Study Completed.'),
                'type': 'success',
                'sticky': False,
            }
        }
