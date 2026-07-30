/** @odoo-module **/

import { registry } from "@web/core/registry";

const DashboardService = {
    orm: null,

    setup(env) {
        this.orm = env.services.orm;
    },

    async getCommercialData() {
        const data = await this.orm.call(
            "hill.dashboard.commercial",
            "get_dashboard_data",
            []
        );

        return {
            ...data,

            monthlyChart: this.buildLineChart(
                "Monthly Cases",
                data.monthly_labels,
                data.monthly_values
            ),

            clientTypeChart: this.buildPieChart(
                "Client Type",
                ["B2B", "B2C"],
                [
                    data.b2b_cases,
                    data.b2c_cases,
                ]
            ),
        };
    },

    async getOperationalData() {
        const data = await this.orm.call(
            "hill.dashboard.operational",
            "get_dashboard_data",
            []
        );

        return {
            ...data,
            agentChart: this.buildBarChart(
                "Open Cases",
                data.agent_labels,
                data.agent_cases
            ),

            technicianChart: this.buildGroupedBarChart(
                data.technician_labels,
                data.planned_visits,
                data.completed_visits,
                data.cancelled_visits
            ),
        };
    },

    async getFinancialData() {
        const data = await this.orm.call(
            "hill.dashboard.financial",
            "get_dashboard_data",
            []
        );

        return {
            ...data,
            revenueChart: this.buildBarChart(
                "Monthly Revenue",
                data.revenue_labels,
                data.revenue_values
            ),
        };
    },

    buildLineChart(label, labels, values) {
        return {
            type: "line",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: label,
                        data: values,
                        borderWidth: 2,
                        tension: 0.4,
                        fill: false,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
            },
        };
    },

    buildPieChart(label, labels, values) {
        return {
            type: "pie",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: label,
                        data: values,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
            },
        };
    },

    buildBarChart(label, labels, values) {
        return {
            type: "bar",
            data: {
                labels,
                datasets: [
                    {
                        label,
                        data: values,
                        borderWidth: 1,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false,
                    },
                },
            },
        };
    },

    buildGroupedBarChart(labels, planned, completed, cancelled) {
        return {
            type: "bar",
            data: {
                labels,
                datasets: [
                    {
                        label: "Planned",
                        data: planned,
                    },
                    {
                        label: "Completed",
                        data: completed,
                    },
                    {
                        label: "Cancelled",
                        data: cancelled,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        stacked: false,
                    },
                    y: {
                        beginAtZero: true,
                    },
                },
            },
        };
    },
};

registry.category("services").add("dashboard_service", {
    start(env) {
        DashboardService.setup(env);
        return DashboardService;
    },
});
