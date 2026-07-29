from collections import defaultdict
from odoo import api, fields, models

class HillOperationalDashboard(models.AbstractModel):
    _name = "hill.dashboard.operational"
    _description = "Operational Dashboard"

    @api.model
    def get_dashboard_data(self):

        Case = self.env["hill.case"]
        SiteReport = self.env["site.report"]

        done_stage = self.env.ref("hill_solution.stage_done")
        tovisit_stage = self.env.ref("hill_solution.stage_tovisit")
        approved_stage = self.env.ref("hill_solution.stage_approved")
        rejected_stage = self.env.ref("hill_solution.stage_rejected")

        # -------------------------------------------------
        # KPI
        # -------------------------------------------------
        total_cases = Case.search_count([])
        completed_cases = Case.search_count([
            ("stage_id", "=", done_stage.id)
        ])

        in_progress_cases = total_cases - completed_cases

        # -------------------------------------------------
        # Cases Per Agent
        # -------------------------------------------------
        agent_map = defaultdict(int)

        for case in Case.search([
            ("agent_name", "!=", False)
        ]):

            if case.stage_id.id == done_stage.id:
                continue

            agent_map[case.agent_name.name] += 1

        # -------------------------------------------------
        # Visits Per Technician
        # -------------------------------------------------
        technician_map = defaultdict(lambda: {
            "planned": 0,
            "completed": 0,
            "cancelled": 0,
        })

        for report in SiteReport.search([]):
            technician = report.technician_name.name if report.technician_name else "Unassigned"

            if report.stage_id.id == tovisit_stage.id:
                technician_map[technician]["planned"] += 1

            elif report.stage_id.id == approved_stage.id:
                technician_map[technician]["completed"] += 1

            elif report.stage_id.id == rejected_stage.id:
                technician_map[technician]["cancelled"] += 1

        # -------------------------------------------------
        # Overdue Cases
        # -------------------------------------------------
        overdue_days = 7
        overdue_cases = []

        for case in Case.search([]):
            if case.stage_id.id == done_stage.id:
                continue

            if not case.write_date:
                continue

            days = (
                fields.Datetime.now() -
                case.write_date
            ).days

            if days >= overdue_days:
                overdue_cases.append({
                    "case_number": case.case_number,
                    "customer": case.partner_id.name or "",
                    "assigned_to": case.agent_name.name or "",
                    "stage": case.stage_id.name or "",
                    "days": days,
                })
        return {
            # KPI
            "total_cases": total_cases,
            "in_progress_cases": in_progress_cases,
            "completed_cases": completed_cases,
            "overdue_count": len(overdue_cases),

            # Cases Per Agent
            "agent_labels": list(agent_map.keys()),
            "agent_cases": list(agent_map.values()),

            # Visits Per Technician
            "technician_labels": list(technician_map.keys()),
            "planned_visits": [
                x["planned"]
                for x in technician_map.values()
            ],
            "completed_visits": [
                x["completed"]
                for x in technician_map.values()
            ],
            "cancelled_visits": [
                x["cancelled"]
                for x in technician_map.values()
            ],

            # Table
            "overdue_cases": overdue_cases,
        }
