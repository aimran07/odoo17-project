import base64
import subprocess
import tempfile
import os
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StudyReportWizard(models.TransientModel):
    _name = 'study.report.wizard'
    _description = 'Study Report Preview Wizard'

    study_id = fields.Many2one('hill.study', string='Study', required=True)
    preview_url = fields.Char('Preview URL')
    preview_html = fields.Html('Preview', sanitize=False, sanitize_attributes=False)
    attachment_id = fields.Many2one('ir.attachment', string='Generated Report')

    def action_open_preview(self):
        self.ensure_one()
        study = self.study_id
        pdf_data = self._generate_pdf(study)
        attachment = self.env['ir.attachment'].create({
            'name': 'study_report_%s.pdf' % study.id,
            'datas': base64.b64encode(pdf_data),
            'mimetype': 'application/pdf',
            'res_model': 'study.report.wizard',
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
            'preview_url': preview_url,
            'preview_html': preview_html,
            'attachment_id': attachment.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'study.report.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }

    def action_save_report(self):
        self.ensure_one()
        study = self.study_id
        if not self.attachment_id:
            raise UserError(_('Please open the preview first.'))
        attachment = self.attachment_id
        attachment.write({
            'res_model': 'hill.study',
            'res_id': study.id,
        })
        self.env['hill.site.document'].create({
            'study_id': study.id,
            'case_id': study.case_id.id,
            'attachment_id': attachment.id,
        })
        study.study_report_saved = True
        study._ensure_esign_document(attachment)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Study report saved to documents.'),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    def _generate_pdf(self, study, signature_image=None, signature_name=None):
        html = self._render_report_html(study, signature_image=signature_image, signature_name=signature_name)
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

    def _render_report_html(self, study, signature_image=None, signature_name=None):
        study.ensure_one()
        partner = ''
        if study.client_type == 'b2b':
            partner = study.company_name or ''
        elif study.client_type == 'b2c':
            first = study.beneficiary_firstname or ''
            last = study.beneficiary_lastname or ''
            partner = ('%s %s' % (first, last)).strip()

        signature_block = ''
        if signature_image and signature_name:
            if isinstance(signature_image, bytes):
                signature_image = signature_image.decode('utf-8')
            signature_block = '''
    <div class="section signature-section">
        <h2>%(signature_label)s</h2>
        <table>
            <tr><td class="label">%(signature_name_label)s</td><td class="value">%(signature_name)s</td></tr>
            <tr><td class="label">%(signature_date_label)s</td><td class="value">%(signature_date)s</td></tr>
            <tr><td colspan="2"><img src="data:image/png;base64,%(signature_image)s" class="signature-image"/></td></tr>
        </table>
    </div>
''' % {
                'signature_label': _('Signature'),
                'signature_name_label': _('Signed By'),
                'signature_name': signature_name,
                'signature_date_label': _('Date'),
                'signature_date': str(fields.Date.today()),
                'signature_image': signature_image,
            }

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
    .signature-section { margin-top: 40px; }
    .signature-image { max-width: 250px; max-height: 100px; }
</style>
</head>
<body>
    <div class="header">
        <h1>%(study_report_label)s</h1>
        <p>%(study_name)s</p>
    </div>

    <div class="section">
        <h2>%(study_info_label)s</h2>
        <table>
            <tr><td class="label">%(study_title_label)s</td><td class="value">%(study_name)s</td></tr>
            <tr><td class="label">%(case_number_label)s</td><td class="value">%(case_number)s</td></tr>
            <tr><td class="label">%(study_nature_label)s</td><td class="value">%(study_nature)s</td></tr>
            <tr><td class="label">%(study_status_label)s</td><td class="value">%(study_status)s</td></tr>
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
        <h2>%(study_data_label)s</h2>
        <div class="notes">%(study_data)s</div>
    </div>

    <div class="section">
        <h2>%(study_notes_label)s</h2>
        <div class="notes">%(study_notes)s</div>
    </div>

    %(signature_block)s
</body>
</html>
''' % {
            'study_report_label': _('Study Report'),
            'study_name': study.name or '',
            'study_info_label': _('Study Information'),
            'study_title_label': _('Study Title'),
            'case_number_label': _('Case Number'),
            'case_number': study.case_number or '',
            'study_nature_label': _('Study Nature'),
            'study_nature': dict(study._fields['study_nature'].selection).get(
                study.study_nature, study.study_nature or ''
            ),
            'study_status_label': _('Study Status'),
            'study_status': dict(study._fields['study_status'].selection).get(
                study.study_status, study.study_status or ''
            ),
            'client_type_label': _('Client Type'),
            'client_type': dict(study._fields['client_type'].selection).get(
                study.client_type, study.client_type or ''
            ),
            'client_info_label': _('Client Information'),
            'client_label': _('Company') if study.client_type == 'b2b' else _('Beneficiary'),
            'partner': partner,
            'site_data_label': _('Site Data'),
            'length_label': _('Length'),
            'length': study.length or '',
            'breadth_label': _('Breadth'),
            'breadth': study.breadth or '',
            'height_label': _('Height'),
            'height': study.height or '',
            'area_label': _('Area'),
            'area': study.area or '',
            'volume_label': _('Volume'),
            'volume': study.volume or '',
            'temperature_label': _('Temperature'),
            'temperature': study.temperature or '',
            'pressure_label': _('Pressure'),
            'pressure': study.pressure or '',
            'study_data_label': _('Study Input Data'),
            'study_data': study.study_data or '',
            'study_notes_label': _('Study Notes'),
            'study_notes': study.study_notes or '',
            'signature_block': signature_block,
        }