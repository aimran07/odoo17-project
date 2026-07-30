from collections import defaultdict
from odoo import api, models

class HillFinancialDashboard(models.AbstractModel):
    _name = "hill.dashboard.financial"
    _description = "Financial Dashboard"

    @api.model
    def get_dashboard_data(self):

        Case = self.env["hill.case"]
        Invoice = self.env["hill.invoice"]

        # -----------------------------------
        # KPI
        # -----------------------------------
        paid_cases = Case.search_count([
            ("payment_status", "=", "paid")
        ])

        unpaid_cases = Case.search_count([
            ("payment_status", "=", "unpaid")
        ])

        awaiting_cases = Case.search_count([
            ("payment_status", "=", "awaiting")
        ])

        total_revenue = sum(
            Invoice.search([]).mapped("amount_total")
        )

        # -----------------------------------
        # Monthly Revenue
        # -----------------------------------
        monthly = defaultdict(float)

        for invoice in Invoice.search([], order="invoice_date"):

            if not invoice.invoice_date:
                continue

            month = invoice.invoice_date.strftime("%b %Y")
            monthly[month] += invoice.amount_total

        # -----------------------------------
        # Invoice List
        # -----------------------------------
        invoices = []

        for invoice in Invoice.search([], order="invoice_date desc"):
            invoices.append({
                "customer": invoice.partner_id.name,
                "invoice_number": invoice.name,
                "date": invoice.invoice_date,
                "amount": invoice.amount_total,
                "status": invoice.state,
            })

        # -----------------------------------
        # Outstanding Per Customer
        # -----------------------------------
        outstanding = defaultdict(int)

        cases = Case.search([
            ("payment_status", "!=", "paid")
        ])

        for case in cases:
            if case.partner_id:
                outstanding[case.partner_id.name] += 1
        outstanding_list = [
            {
                "customer": customer,
                "cases": count,
            }
            for customer, count in outstanding.items()
        ]

        return {
            "paid_cases": paid_cases,
            "unpaid_cases": unpaid_cases,
            "awaiting_cases": awaiting_cases,
            "total_revenue": total_revenue,
            "revenue_labels": list(monthly.keys()),
            "revenue_values": list(monthly.values()),
            "invoices": invoices,
            "outstanding": outstanding_list,
        }
