import base64
import io
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

from odoo import api, models, fields


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

    is_webcam_capture = fields.Boolean(
        string='Webcam Capture',
        default=False,
    )
    geo_latitude = fields.Float(
        string='Latitude',
        digits=(9, 6),
    )
    geo_longitude = fields.Float(
        string='Longitude',
        digits=(9, 6),
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

    _FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    _TIMEZONE = ZoneInfo('Europe/Paris')

    @api.model_create_multi
    def create(self, vals_list):
        records = super(HillSitePhoto, self).create(vals_list)
        for rec in records:
            if rec.is_webcam_capture:
                rec._stamp_metadata()
        return records

    def _stamp_metadata(self):
        self.ensure_one()
        attachment = self.attachment_id
        if not attachment or not attachment.datas:
            return
        try:
            image = Image.open(io.BytesIO(base64.b64decode(attachment.datas))).convert('RGB')
        except Exception:
            return

        draw = ImageDraw.Draw(image, 'RGBA')
        width, height = image.size
        scale = max(0.5, min(1.2, width / 1200.0))

        lines = [self._timestamp_label()]
        coords = self._coords_label()
        if coords:
            lines.append(coords)

        font_size = int(round(20 * scale))
        font = ImageFont.truetype(self._FONT_PATH, font_size)
        pad = int(round(12 * scale))
        line_height = int(round(font_size * 1.35))

        text_widths = [draw.textbbox((0, 0), line, font=font)[2] for line in lines]
        box_width = max(text_widths) + 2 * pad
        box_height = line_height * len(lines) + pad

        x0 = width - box_width
        y0 = height - box_height
        draw.rectangle([x0, y0, width, height], fill=(0, 0, 0, 140))

        y = y0 + pad / 2
        for line in lines:
            draw.text((x0 + pad, y), line, font=font, fill=(255, 255, 255, 255))
            y += line_height

        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=90)
        attachment.write({'datas': base64.b64encode(buffer.getvalue())})

    def _timestamp_label(self):
        self.ensure_one()
        if not self.uploaded_at:
            return ''
        utc_value = fields.Datetime.from_string(self.uploaded_at).replace(tzinfo=ZoneInfo('UTC'))
        return utc_value.astimezone(self._TIMEZONE).strftime('%d/%m/%Y %H:%M:%S')

    def _coords_label(self):
        self.ensure_one()
        if self.geo_latitude is None or self.geo_longitude is None:
            return ''
        ns = 'N' if self.geo_latitude >= 0 else 'S'
        ew = 'E' if self.geo_longitude >= 0 else 'W'
        return '%.5f\u00b0 %s, %.5f\u00b0 %s' % (
            abs(self.geo_latitude), ns, abs(self.geo_longitude), ew)