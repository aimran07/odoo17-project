{
    'name': 'Hill Solution',
    'version': '17.0.1.2.0',
    'category': 'Services',
    'summary': 'Manage service cases with kanban and tree views',
    'description': """
Hill Solution Module
====================
Features:
- Case management with Kanban and Tree views
- Stages: New Case, Technician Assigned, Visit Completed, Visit Cancelled
- Unique case number via sequence
- Form view with title and details
- Menu: Cases
""",
    'author': 'Your Company',
    'depends': ['base', 'mail', 'hr', 'website', 'portal'],
    'data': [
        'security/hill_case_security.xml',
        'security/hide_default_menus.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/invoice_sequence.xml',                    # new added
        'data/hill_case_stage_data.xml',
        'data/site_report_stage_data.xml',
        'data/hill_study_stage_data.xml',
        'views/hill_case_views.xml',
        'views/site_report_views.xml',
        'views/site_report_wizard_views.xml',
        'views/hill_study_views.xml',
        'views/hill_payment_register_wizard_views.xml',
        'views/hill_visit_wizard_views.xml',
        'views/res_partner_invoice_views.xml',          # new added
        'views/hill_invoice_views.xml',                 # new added
        'views/invoice_generation_wizard_views.xml',    # new added
        'report/invoice_report.xml',                    # new added
        'report/invoice_report_template.xml',           # new added
        'views/hill_case_menu.xml',
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hill_solution/static/src/css/hill_case_kanban.css',
            'hill_solution/static/src/css/hill_document_widget.css',
            'hill_solution/static/src/css/hill_photo_widget.css',
            'hill_solution/static/src/css/site_report_wizard.css',
            'hill_solution/static/src/css/visit_date_widget.css',

            'hill_solution/static/src/js/hill_document_widget.js',
            'hill_solution/static/src/js/hill_photo_widget.js',
            'hill_solution/static/src/js/visit_date_widget.js',

            'hill_solution/static/src/xml/hill_document_widget.xml',
            'hill_solution/static/src/xml/hill_photo_widget.xml',
            'hill_solution/static/src/xml/visit_date_widget.xml',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
} # type: ignore
