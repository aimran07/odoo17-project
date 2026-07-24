{
    "name": "Demo Collapsible Form",
    "version": "17.0.1.0",
    "depends": ["base", "web"],

    "data": [
        "security/ir.model.access.csv",
        "views/demo_record_views.xml",
    ],

    "assets": {
        "web.assets_backend": [
            "collapsible_form_demo/static/src/js/collapsible.js",
            "collapsible_form_demo/static/src/css/collapsible.css",
        ],
    },

    "installable": True,
}
