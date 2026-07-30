/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

import { DashboardKpiCard }
from "../../components/dashboard_kpi_card/dashboard_kpi_card";

import { DashboardChart }
from "../../components/dashboard_chart/dashboard_chart";

export class OperationalDashboard extends Component {

    static template = "hill_dashboard.OperationalDashboard";

    static components = {
        DashboardKpiCard,
        DashboardChart,
    };

    setup() {
        this.dashboard = useService("dashboard_service");

        this.state = useState({
            loading: true,
            data: {},
        });

        onWillStart(async () => {
            this.state.data =
                await this.dashboard.getOperationalData();

            this.state.loading = false;
        });
    }
}

registry.category("actions").add(
    "hill_dashboard.operational_dashboard",
    OperationalDashboard
);
