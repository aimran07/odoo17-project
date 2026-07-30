# -*- coding: utf-8 -*-
# from odoo import http


# class HillDashboard(http.Controller):
#     @http.route('/hill_dashboard/hill_dashboard', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hill_dashboard/hill_dashboard/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hill_dashboard.listing', {
#             'root': '/hill_dashboard/hill_dashboard',
#             'objects': http.request.env['hill_dashboard.hill_dashboard'].search([]),
#         })

#     @http.route('/hill_dashboard/hill_dashboard/objects/<model("hill_dashboard.hill_dashboard"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hill_dashboard.object', {
#             'object': obj
#         })

