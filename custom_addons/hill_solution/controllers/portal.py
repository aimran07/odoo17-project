import base64
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError


class HillCasePortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'case_count' in counters:
            values['case_count'] = request.env['hill.case'].search_count(
                self._get_case_domain()
            )
        if 'invoice_count' in counters:
            values['invoice_count'] = request.env['hill.invoice'].search_count(
                self._get_invoice_domain()
            )
        return values

    def _get_case_domain(self):
        partner = request.env.user.partner_id
        return [('partner_id', '=', partner.id)]

    def _get_invoice_domain(self):
        partner = request.env.user.partner_id
        return [
            ('partner_id', '=', partner.id),
            ('state', 'in', ['generated', 'paid']),
        ]

    # ── Profile page ──────────────────────────────────────────────────────────

    @http.route('/my/account', type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        partner = request.env.user.partner_id

        values = self._prepare_portal_layout_values()
        values.update({
            'partner': partner,
            'redirect': redirect,
            'error': {},
            'error_message': [],
            'success': False,
            'page_name': 'my_details',
        })

        if post and request.httprequest.method == 'POST':
            client_type = post.get('hill_client_type')

            allowed_keys = (
                'hill_client_type',
                'hill_contact_firstname', 'hill_contact_lastname',
                'hill_company_name', 'hill_b2b_phone', 'hill_siret',
                'hill_beneficiary_firstname', 'hill_beneficiary_lastname',
                'hill_beneficiary_phone', 'hill_beneficiary_status',
                'name', 'phone', 'email', 'street',
                'city', 'zipcode', 'state_id', 'country_id', 'vat',
                'redirect', 'csrf_token',
            )
            unknown = [k for k in post if k not in allowed_keys]
            if unknown:
                values['error']['common'] = 'Unknown field'
                values['error_message'] = ["Unknown field '%s'" % ','.join(unknown)]
                return request.render('portal.portal_my_details', values)

            # Step 1 — only client type selected, no other hill fields submitted yet
            hill_data_keys = (
                'hill_contact_firstname', 'hill_contact_lastname',
                'hill_company_name', 'hill_b2b_phone', 'hill_siret',
                'hill_beneficiary_firstname', 'hill_beneficiary_lastname',
                'hill_beneficiary_phone', 'hill_beneficiary_status',
            )
            only_type_submitted = not any(k in post for k in hill_data_keys)

            if only_type_submitted and client_type and not partner.hill_client_type:
                partner.sudo().write({'hill_client_type': client_type})
                return request.redirect('/my/account')

            # If client type is already set and only the hidden input is posted,
            # or if no client_type at all in post (shouldn't happen), keep existing
            if not client_type:
                client_type = partner.hill_client_type

            # Step 2 — full form submitted (or re-saving existing profile)
            error = {}
            error_message = []
            client_type = client_type or partner.hill_client_type

            if client_type == 'b2b':
                if not post.get('hill_contact_firstname'):
                    error['hill_contact_firstname'] = 'missing'
                if not post.get('hill_company_name'):
                    error['hill_company_name'] = 'missing'
                if not post.get('hill_b2b_phone'):
                    error['hill_b2b_phone'] = 'missing'
            elif client_type == 'b2c':
                if not post.get('hill_beneficiary_firstname'):
                    error['hill_beneficiary_firstname'] = 'missing'
                if not post.get('hill_beneficiary_phone'):
                    error['hill_beneficiary_phone'] = 'missing'
            else:
                error['hill_client_type'] = 'missing'

            if error:
                values['error'] = error
                values['error_message'] = error_message or ['Some required fields are empty.']
                values.update(post)
                return request.render('portal.portal_my_details', values)

            vals = {
                'hill_client_type': client_type,
            }
            if client_type == 'b2b':
                vals.update({
                    'hill_contact_firstname': post.get('hill_contact_firstname', ''),
                    'hill_contact_lastname': post.get('hill_contact_lastname', ''),
                    'hill_company_name': post.get('hill_company_name', ''),
                    'hill_b2b_phone': post.get('hill_b2b_phone', ''),
                    'hill_siret': post.get('hill_siret', ''),
                })
            elif client_type == 'b2c':
                vals.update({
                    'hill_beneficiary_firstname': post.get('hill_beneficiary_firstname', ''),
                    'hill_beneficiary_lastname': post.get('hill_beneficiary_lastname', ''),
                    'hill_beneficiary_phone': post.get('hill_beneficiary_phone', ''),
                    'hill_beneficiary_status': post.get('hill_beneficiary_status', 'standard'),
                })

            # Keep Odoo default fields if present
            for fname in ('name', 'phone', 'email', 'street',
                          'city', 'zipcode', 'state_id', 'country_id', 'vat'):
                if fname in post:
                    vals[fname] = post[fname]
            if 'zipcode' in vals:
                vals['zip'] = vals.pop('zipcode')
            for field in ('country_id', 'state_id'):
                if field in vals:
                    try:
                        vals[field] = int(vals[field])
                    except (ValueError, TypeError):
                        vals[field] = False

            partner.sudo().write(vals)
            values['success'] = True
            if redirect:
                return request.redirect(redirect)
            return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        values.update({
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'partner_can_edit_vat': partner.can_edit_vat(),
            'hill_client_type': partner.hill_client_type,
            'hill_contact_firstname': partner.hill_contact_firstname,
            'hill_contact_lastname': partner.hill_contact_lastname,
            'hill_company_name': partner.hill_company_name,
            'hill_b2b_phone': partner.hill_b2b_phone,
            'hill_siret': partner.hill_siret,
            'hill_beneficiary_firstname': partner.hill_beneficiary_firstname,
            'hill_beneficiary_lastname': partner.hill_beneficiary_lastname,
            'hill_beneficiary_phone': partner.hill_beneficiary_phone,
            'hill_beneficiary_status': partner.hill_beneficiary_status,
        })

        response = request.render('portal.portal_my_details', values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    # ── Case list ─────────────────────────────────────────────────────────────

    @http.route(
        ['/my/cases', '/my/cases/page/<int:page>'],
        type='http',
        auth='user',
        website=True,
    )
    def portal_my_cases(self, page=1, **kwargs):
        domain = self._get_case_domain()
        Case = request.env['hill.case']
        case_count = Case.search_count(domain)
        pager = portal_pager(
            url='/my/cases',
            total=case_count,
            page=page,
            step=10,
        )
        cases = Case.search(
            domain,
            order='create_date desc',
            limit=10,
            offset=pager['offset'],
        )
        return request.render('hill_solution.portal_my_cases', {
            'cases': cases,
            'page_name': 'cases',
            'pager': pager,
        })

    # ── Case detail ───────────────────────────────────────────────────────────

    @http.route(
        '/my/cases/<int:case_id>',
        type='http',
        auth='user',
        website=True,
    )
    def portal_case_detail(self, case_id, **kwargs):
        try:
            case = self._document_check_access('hill.case', case_id)
        except (AccessError, MissingError):
            return request.redirect('/my/cases')
        return request.render('hill_solution.portal_case_detail', {
            'case': case,
            'page_name': 'cases',
        })

    # ── Invoice list ───────────────────────────────────────────────────────

    @http.route(
        ['/my/invoices', '/my/invoices/page/<int:page>'],
        type='http',
        auth='user',
        website=True,
    )
    def portal_my_invoices(self, page=1, **kwargs):
        domain = self._get_invoice_domain()
        Invoice = request.env['hill.invoice']
        invoice_count = Invoice.search_count(domain)
        pager = portal_pager(
            url='/my/invoices',
            total=invoice_count,
            page=page,
            step=10,
        )
        invoices = Invoice.search(
            domain,
            order='create_date desc',
            limit=10,
            offset=pager['offset'],
        )
        return request.render('hill_solution.portal_my_invoices', {
            'invoices': invoices,
            'page_name': 'invoices',
            'pager': pager,
        })

    # ── Invoice detail ─────────────────────────────────────────────────────

    @http.route(
        '/my/invoices/<int:invoice_id>',
        type='http',
        auth='user',
        website=True,
    )
    def portal_invoice_detail(self, invoice_id, **kwargs):
        try:
            invoice = self._document_check_access('hill.invoice', invoice_id)
        except (AccessError, MissingError):
            return request.redirect('/my/invoices')
        return request.render('hill_solution.portal_invoice_detail', {
            'invoice': invoice,
            'page_name': 'invoices',
        })

    # ── Invoice download (on-the-fly PDF) ───────────────────────────────────

    @http.route(
        '/my/invoices/<int:invoice_id>/download',
        type='http',
        auth='user',
        website=True,
    )
    def portal_invoice_download(self, invoice_id, **kwargs):
        try:
            invoice = self._document_check_access('hill.invoice', invoice_id)
        except (AccessError, MissingError):
            return request.redirect('/my/invoices')

        report = request.env.ref('hill_solution.action_invoice_report')
        pdf, _ = report.sudo()._render_qweb_pdf(report, invoice.ids)
        headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition',
             "attachment; filename=\"%s.pdf\"" % invoice.name),
        ]
        return request.make_response(pdf, headers=headers)

    # ── New case form ─────────────────────────────────────────────────────────

    @http.route(
        '/my/cases/new',
        type='http',
        auth='user',
        website=True,
    )
    def portal_case_new(self, **kwargs):
        partner = request.env.user.partner_id

        if not partner.hill_client_type:
            return request.render('portal.portal_my_details', {
                'page_name': 'my_details',
                'partner': partner,
                'error': {'hill_client_type': 'missing'},
                'error_message': ['Please select your client type first.'],
                'redirect': '/my/cases/new',
            })

        return request.render('hill_solution.portal_case_form', {
            'page_name': 'cases',
            'error': {},
            'post': {},
            'client_type': partner.hill_client_type,
            'partner': partner,
        })

    # ── Case form submit ──────────────────────────────────────────────────────

    @http.route(
        '/my/cases/submit',
        type='http',
        auth='user',
        website=True,
        methods=['POST'],
        csrf=True,
    )
    def portal_case_submit(self, **post):
        partner = request.env.user.partner_id
        client_type = partner.hill_client_type

        if not client_type:
            return request.redirect('/my/account')

        error = {}

        address = None
        if client_type == 'b2b':
            address = post.get('site_address')
            if not address:
                error['site_address'] = 'Site address is required.'
        elif client_type == 'b2c':
            address = post.get('residential_address')
            if not address:
                error['residential_address'] = 'Residential address is required.'

        if error:
            return request.render('hill_solution.portal_case_form', {
                'page_name': 'cases',
                'error': error,
                'post': post,
                'client_type': client_type,
                'partner': partner,
            })

        vals = {
            'client_type': client_type,
            'partner_id': partner.id,
            'service_type': post.get('service_type') or False,
        }

        if client_type == 'b2b':
            vals.update({
                'company_name': partner.hill_company_name,
                'contact_firstname': partner.hill_contact_firstname,
                'contact_lastname': partner.hill_contact_lastname,
                'b2b_phone': partner.hill_b2b_phone,
                'siret': partner.hill_siret,
                'site_address': address,
            })
        elif client_type == 'b2c':
            vals.update({
                'beneficiary_firstname': partner.hill_beneficiary_firstname,
                'beneficiary_lastname': partner.hill_beneficiary_lastname,
                'beneficiary_phone': partner.hill_beneficiary_phone,
                'beneficiary_status': partner.hill_beneficiary_status,
                'residential_address': address,
            })

        case = request.env['hill.case'].sudo().create(vals)

        # Handle document uploads
        if 'documents' in request.httprequest.files:
            document_files = request.httprequest.files.getlist('documents')
            for file_data in document_files:
                if file_data and file_data.filename:
                    attachment = request.env['ir.attachment'].sudo().create({
                        'name': file_data.filename,
                        'type': 'binary',
                        'datas': base64.b64encode(file_data.read()),
                        'res_model': 'hill.case',
                        'res_id': case.id,
                        'mimetype': file_data.content_type or 'application/octet-stream',
                    })
                    attachment.sudo().generate_access_token()
                    request.env['hill.site.document'].sudo().create({
                        'case_id': case.id,
                        'attachment_id': attachment.id,
                    })
                    attachment.sudo().generate_access_token()

        return request.redirect(f'/my/cases/{case.id}')
