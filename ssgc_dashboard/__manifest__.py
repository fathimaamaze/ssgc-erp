# -*- coding: utf-8 -*-
{
    'name': "SSGC Dashboard",
    'version': '17.0.0.0',
    'author': '',
    'website': "",
    'category': '',
    'summary': "",
    'description': "",
    'depends': ['base', 'pragtech_purchase', 'pragtech_purchase_reports'],
    'data': [
        'views/views.xml',
        'views/menu_items.xml',

    ],
    "assets": {
        "web.assets_backend": [
            "ssgc_dashboard/static/src/xml/templates.xml",
            # "ssgc_dashboard/static/src/xml/execution_dashboard.xml",
            "ssgc_dashboard/static/src/xml/dashboard_view.xml",
            "ssgc_dashboard/static/src/css/dashboard_view.css",
            "ssgc_dashboard/static/src/css/dashboard_view.scss",
            "ssgc_dashboard/static/src/xml/execution_dashboard.xml",
            "ssgc_dashboard/static/src/xml/dashboard_view.xml",
            "ssgc_dashboard/static/src/js/btn_listview.js",
            "ssgc_dashboard/static/src/js/dashboard_view.js",
            # "ssgc_dashboard/static/src/js/execution_dashboard.js",
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
