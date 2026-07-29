{
    "name": "Hill Dashboard",
    "version": "17.0.1.0.0",
    "summary": "Dashboard and Analytics for Hill Solution",
    "description": """
Hill Dashboard
==============
Commercial, Operational and Financial dashboards
for Hill Solution.
""",
    "author": "Your Company",
    "category": "Services",
    "license": "LGPL-3",
    "application": True,
    "installable": True,

    "depends": [
        "web",
        "hill_solution",
    ],

    "data": [
        "security/ir.model.access.csv",
        "views/dashboard_menu.xml",
    ],

    "assets": {
        "web.assets_backend": [
            # Third-party libraries
            'hill_dashboard/static/vendor/chartjs/chart.umd.js',

            # Services
            "hill_dashboard/static/src/services/dashboard_service.js",

            # Components
            "hill_dashboard/static/src/components/dashboard_kpi_card/dashboard_kpi_card.js",
            "hill_dashboard/static/src/components/dashboard_kpi_card/dashboard_kpi_card.xml",
            "hill_dashboard/static/src/components/dashboard_kpi_card/dashboard_kpi_card.css",

            "hill_dashboard/static/src/components/dashboard_chart/dashboard_chart.js",
            "hill_dashboard/static/src/components/dashboard_chart/dashboard_chart.xml",
            "hill_dashboard/static/src/components/dashboard_chart/dashboard_chart.css",

            # Dashboards
            "hill_dashboard/static/src/dashboards/commercial/commercial_dashboard.js",
            "hill_dashboard/static/src/dashboards/commercial/commercial_dashboard.xml",

            "hill_dashboard/static/src/dashboards/operational/operational_dashboard.js",
            "hill_dashboard/static/src/dashboards/operational/operational_dashboard.xml",

            "hill_dashboard/static/src/dashboards/financial/financial_dashboard.js",
            "hill_dashboard/static/src/dashboards/financial/financial_dashboard.xml",

            # Global CSS
            "hill_dashboard/static/src/css/dashboard.css",
        ],
    },
}
