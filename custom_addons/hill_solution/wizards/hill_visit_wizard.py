from odoo import models, fields, api, _


class HillVisitWizard(models.TransientModel):
    _name = 'hill.visit.wizard'
    _description = 'Create Site Visit Wizard'

    case_id = fields.Many2one(
        'hill.case',
        string='Case',
        required=True,
    )

    client_type = fields.Selection(
        related='case_id.client_type',
        string='Client Type',
        readonly=True,
    )
    service_type = fields.Char(
        string='Service Type',
        compute='_compute_service_type',
        readonly=True,
    )
    case_number = fields.Char(
        related='case_id.case_number',
        string='Case Number',
        readonly=True,
    )

    @api.depends('case_id.service_type')
    def _compute_service_type(self):
        for wizard in self:
            service_type = wizard.case_id.service_type
            if not service_type:
                wizard.service_type = ''
                continue
            selection = dict(
                wizard.case_id._fields['service_type'].selection
            )
            wizard.service_type = selection.get(service_type, service_type)

    company_name = fields.Char(
        related='case_id.company_name',
        string='Company Name',
        readonly=True,
    )
    contact_firstname = fields.Char(
        related='case_id.contact_firstname',
        string='Contact First Name',
        readonly=True,
    )
    contact_lastname = fields.Char(
        related='case_id.contact_lastname',
        string='Contact Last Name',
        readonly=True,
    )
    b2b_phone = fields.Char(
        related='case_id.b2b_phone',
        string='Phone Number',
        readonly=True,
    )
    siret = fields.Char(
        related='case_id.siret',
        string='SIRET Number',
        readonly=True,
    )
    site_address = fields.Text(
        related='case_id.site_address',
        string='Site Address',
        readonly=True,
    )

    beneficiary_firstname = fields.Char(
        related='case_id.beneficiary_firstname',
        string='Beneficiary First Name',
        readonly=True,
    )
    beneficiary_lastname = fields.Char(
        related='case_id.beneficiary_lastname',
        string='Beneficiary Last Name',
        readonly=True,
    )
    beneficiary_phone = fields.Char(
        related='case_id.beneficiary_phone',
        string='Phone Number',
        readonly=True,
    )
    beneficiary_status = fields.Selection(
        related='case_id.beneficiary_status',
        string='Beneficiary Status',
        readonly=True,
    )
    residential_address = fields.Text(
        related='case_id.residential_address',
        string='Residential Address',
        readonly=True,
    )

    technician_name = fields.Many2one(
        'hr.employee',
        string='Technician',
        required=True,
    )
    visit_date = fields.Datetime(
        string='Visit Date',
        required=True,
    )
    # visit_duration = fields.Float(
    #     string='Duration (hours)',
    #     default=2.0,
    # )
    # visit_notes = fields.Html(
    #     string='Visit Notes / Report',
    # )

    def action_confirm(self):
        self.ensure_one()
        case = self.case_id

        default_stage = self.env.ref(
            'hill_solution.stage_tovisit', raise_if_not_found=False
        )
        visit_values = {
            'case_id': case.id,
            'name': case.name or _('Site Visit'),
            'technician_name': self.technician_name.id,
            'stage_id': default_stage.id if default_stage else False,
            'client_type': case.client_type,
            'service_type': case.service_type,
            'is_visit_required': case.is_visit_required,
            'company_name': case.company_name,
            'contact_firstname': case.contact_firstname,
            'contact_lastname': case.contact_lastname,
            'b2b_phone': case.b2b_phone,
            'siret': case.siret,
            'site_address': case.site_address or case.residential_address,
            'beneficiary_firstname': case.beneficiary_firstname,
            'beneficiary_lastname': case.beneficiary_lastname,
            'beneficiary_phone': case.beneficiary_phone,
            'beneficiary_status': case.beneficiary_status,
            'residential_address': case.residential_address,
            'visit_date': self.visit_date,
            # 'visit_duration': self.visit_duration,
        }
        self.env['site.report'].create(visit_values)

        case.write({
            'technician_name': self.technician_name.id,
            'visit_date': self.visit_date,
        })

        visit_stage = self.env.ref(
            'hill_solution.stage_visit',
            raise_if_not_found=False,
        )
        if visit_stage:
            case.stage_id = visit_stage.id

        return {'type': 'ir.actions.act_window_close'}
