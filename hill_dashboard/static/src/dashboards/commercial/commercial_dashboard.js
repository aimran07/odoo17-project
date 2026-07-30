/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

import { DashboardKpiCard } from "../../components/dashboard_kpi_card/dashboard_kpi_card";
import { DashboardChart } from "../../components/dashboard_chart/dashboard_chart";

export class CommercialDashboard extends Component {
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
                await this.dashboard.getCommercialData();
            this.state.loading = false;
        });
    }
}

CommercialDashboard.template = "hill_dashboard.CommercialDashboard";

registry.category("actions").add(
    "hill_dashboard.commercial_dashboard",
    CommercialDashboard
);
