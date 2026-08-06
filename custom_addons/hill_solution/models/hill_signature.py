from odoo import fields, models


class HillSignature(models.Model):
    _name = 'hill.signature'
    _description = 'Stored Signature Image'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    image = fields.Binary(string='Signature Image', required=True)
    image_filename = fields.Char(string='Image Filename')
