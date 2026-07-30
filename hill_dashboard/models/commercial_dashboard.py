from collections import defaultdict
from odoo import api, models

class HillCommercialDashboard(models.AbstractModel):
    _name = "hill.dashboard.commercial"
    _description = "Commercial Dashboard"

    @api.model
    def get_dashboard_data(self):

        Case = self.env["hill.case"]
        total_cases = Case.search_count([])

        b2b_cases = Case.search_count([
            ("client_type", "=", "b2b")
        ])

        b2c_cases = Case.search_count([
            ("client_type", "=", "b2c")
        ])

        active_clients = len(
            Case.search([]).mapped("partner_id")
        )

        monthly = defaultdict(int)

        for case in Case.search([], order="create_date"):

            month = case.create_date.strftime("%b %Y")
            monthly[month] += 1

        # Customer-wise summary
        client_summary = {}

        for case in Case.search([]):
            partner = case.partner_id
            if not partner:
                continue

            if partner.id not in client_summary:
                client_summary[partner.id] = {
                    "name": partner.name,
                    "cases": 0,
                    "client_type": (
                        case.client_type.upper()
                        if case.client_type else ""
                    ),
                }

            client_summary[partner.id]["cases"] += 1

        return {
            "total_cases": total_cases,
            "b2b_cases": b2b_cases,
            "b2c_cases": b2c_cases,
            "active_clients": active_clients,
            "monthly_labels": list(monthly.keys()),
            "monthly_values": list(monthly.values()),
            "clients": list(client_summary.values()),
        }
