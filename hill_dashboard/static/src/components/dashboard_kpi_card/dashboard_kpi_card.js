/** @odoo-module **/

import { Component } from "@odoo/owl";

export class DashboardKpiCard extends Component {}

DashboardKpiCard.template = "hill_dashboard.DashboardKpiCard";

DashboardKpiCard.props = {
    title: String,
    value: [String, Number],
    color: {
        type: String,
        optional: true,
    },
    icon: {
        type: String,
        optional: true,
    },
};

DashboardKpiCard.defaultProps = {
    color: "purple",
    icon: "",
};
