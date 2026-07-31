import base64
import subprocess
import tempfile
import os
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SiteReportWizard(models.TransientModel):
    _name = 'site.report.wizard'
    _description = 'Visit Report Preview Wizard'

    site_report_id = fields.Many2one('site.report', string='Site Report', required=True)
    state = fields.Selection([('form', 'Form'), ('preview', 'Preview')], default='form')
    preview_url = fields.Char('Preview URL')
    preview_html = fields.Html('Preview', sanitize=False, sanitize_attributes=False)
    attachment_id = fields.Many2one('ir.attachment', string='Generated Report')

    def action_open_preview(self):
        self.ensure_one()
        report = self.site_report_id
        pdf_data = self._generate_pdf(report)
        attachment = self.env['ir.attachment'].create({
            'name': 'visit_report_%s.pdf' % report.id,
            'datas': base64.b64encode(pdf_data),
            'mimetype': 'application/pdf',
            'res_model': 'site.report.wizard',
            'res_id': self.id,
        })
        preview_url = '/web/content/%s?download=false' % attachment.id
        preview_html = '''
<div style="width:100%%; height:80vh; display:flex;">
    <iframe src="%s"
            style="width:100%%; height:100%%; border:none; flex:1;"
            allowfullscreen>
    </iframe>
</div>''' % preview_url
        self.write({
            'state': 'preview',
            'preview_url': preview_url,
            'preview_html': preview_html,
            'attachment_id': attachment.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'site.report.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }

    def action_save_report(self):
        self.ensure_one()
        report = self.site_report_id
        if not self.attachment_id:
            raise UserError(_('Please open the preview first.'))
        attachment = self.attachment_id
        attachment.write({
            'res_model': 'site.report',
            'res_id': report.id,
        })
        self.env['hill.site.document'].create({
            'site_report_id': report.id,
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

    def action_back(self):
        self.ensure_one()
        self.state = 'form'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'site.report.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }

    def _generate_pdf(self, report):
        html = self._render_report_html(report)
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

    def _render_report_html(self, report):
        report.ensure_one()
        partner = ''
        if report.client_type == 'b2b':
            partner = (
                report.company_name or ''
            )
        elif report.client_type == 'b2c':
            first = report.beneficiary_firstname or ''
            last = report.beneficiary_lastname or ''
            partner = ('%s %s' % (first, last)).strip()

        return '''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
    body { font-family: Arial, sans-serif; font-size: 12pt; color: #333; margin: 0; padding: 0; }
    .header { text-align: center; border-bottom: 2px solid #2E86C1; padding-bottom: 10px; margin-bottom: 20px; }
    .header h1 { color: #2E86C1; font-size: 20pt; margin: 0; }
    .header p { color: #666; font-size: 10pt; margin: 5px 0 0; }
    .section { margin-bottom: 20px; }
    .section h2 { font-size: 13pt; color: #2E86C1; border-bottom: 1px solid #ddd; padding-bottom: 4px; margin: 0 0 10px; }
    table { width: 100%%; border-collapse: collapse; }
    table td { padding: 4px 8px; vertical-align: top; }
    .label { font-weight: bold; color: #555; width: 35%%; }
    .value { color: #333; }
    .notes { background: #f9f9f9; padding: 10px; border-radius: 4px; margin-top: 10px; }
</style>
</head>
<body>
    <div class="header">
        <h1>%(visit_report_label)s</h1>
        <p>%(report_name)s</p>
    </div>

    <div class="section">
        <h2>%(case_info_label)s</h2>
        <table>
            <tr><td class="label">%(case_number_label)s</td><td class="value">%(case_number)s</td></tr>
            <tr><td class="label">%(technician_label)s</td><td class="value">%(technician)s</td></tr>
            <tr><td class="label">%(visit_date_label)s</td><td class="value">%(visit_date)s</td></tr>
            <tr><td class="label">%(service_type_label)s</td><td class="value">%(service_type)s</td></tr>
            <tr><td class="label">%(client_type_label)s</td><td class="value">%(client_type)s</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>%(client_info_label)s</h2>
        <table>
            <tr><td class="label">%(client_label)s</td><td class="value">%(partner)s</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>%(site_data_label)s</h2>
        <table>
            <tr><td class="label">%(length_label)s</td><td class="value">%(length)s</td></tr>
            <tr><td class="label">%(breadth_label)s</td><td class="value">%(breadth)s</td></tr>
            <tr><td class="label">%(height_label)s</td><td class="value">%(height)s</td></tr>
            <tr><td class="label">%(area_label)s</td><td class="value">%(area)s</td></tr>
            <tr><td class="label">%(volume_label)s</td><td class="value">%(volume)s</td></tr>
            <tr><td class="label">%(temperature_label)s</td><td class="value">%(temperature)s</td></tr>
            <tr><td class="label">%(pressure_label)s</td><td class="value">%(pressure)s</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>%(visit_notes_label)s</h2>
        <div class="notes">%(visit_notes)s</div>
    </div>
</body>
</html>
''' % {
            'visit_report_label': _('Visit Report'),
            'report_name': report.name or '',
            'case_info_label': _('Case Information'),
            'case_number_label': _('Case Number'),
            'case_number': report.case_number or '',
            'technician_label': _('Technician'),
            'technician': report.technician_name.name if report.technician_name else '',
            'visit_date_label': _('Visit Date'),
            'visit_date': str(report.visit_date) if report.visit_date else '',
            'service_type_label': _('Service Type'),
            'service_type': dict(report._fields['service_type'].selection).get(report.service_type, report.service_type or ''),
            'client_type_label': _('Client Type'),
            'client_type': dict(report._fields['client_type'].selection).get(report.client_type, report.client_type or ''),
            'client_info_label': _('Client Information'),
            'client_label': _('Company') if report.client_type == 'b2b' else _('Beneficiary'),
            'partner': partner,
            'site_data_label': _('Site Data'),
            'length_label': _('Length'),
            'length': report.length or '',
            'breadth_label': _('Breadth'),
            'breadth': report.breadth or '',
            'height_label': _('Height'),
            'height': report.height or '',
            'area_label': _('Area'),
            'area': report.area or '',
            'volume_label': _('Volume'),
            'volume': report.volume or '',
            'temperature_label': _('Temperature'),
            'temperature': report.temperature or '',
            'pressure_label': _('Pressure'),
            'pressure': report.pressure or '',
            'visit_notes_label': _('Visit Notes'),
            'visit_notes': report.visit_notes or '',
        }
