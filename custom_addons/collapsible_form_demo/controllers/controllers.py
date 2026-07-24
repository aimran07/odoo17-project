# -*- coding: utf-8 -*-
# from odoo import http


# class CollapsibleFormDemo(http.Controller):
#     @http.route('/collapsible_form_demo/collapsible_form_demo', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/collapsible_form_demo/collapsible_form_demo/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('collapsible_form_demo.listing', {
#             'root': '/collapsible_form_demo/collapsible_form_demo',
#             'objects': http.request.env['collapsible_form_demo.collapsible_form_demo'].search([]),
#         })

#     @http.route('/collapsible_form_demo/collapsible_form_demo/objects/<model("collapsible_form_demo.collapsible_form_demo"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('collapsible_form_demo.object', {
#             'object': obj
#         })

