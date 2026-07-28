from odoo import http
from odoo.http import request


class HillAvailabilityController(http.Controller):

    @http.route(
        '/hill_solution/technician_booked_dates',
        type='json',
        auth='user',
    )
    def technician_booked_dates(self, technician_id):
        if not technician_id:
            return []
        visits = request.env['site.report'].search_read(
            [('technician_name', '=', technician_id),
             ('visit_date', '!=', False)],
            ['visit_date'],
        )
        dates = set()
        for v in visits:
            if v['visit_date']:
                dates.add(v['visit_date'].strftime('%Y-%m-%d'))
        return list(dates)
