"""
State Variables
Copyright (c) 2022 Cannabis Data
Copyright (c) 2021-2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 10/15/2020
Updated: 11/23/2022
License: MIT License <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>

Description: Relatively static page context data.
"""
# pylint:disable=line-too-long
from dashboard.settings import DEFAULT_FROM_EMAIL

#-----------------------------------------------------------------------
# Main app context
#-----------------------------------------------------------------------

app_context = {
    'app_name': 'Cannabis Data',
    'contact_email': DEFAULT_FROM_EMAIL,
    'contact_phone': '',
    'contact_phone_number': '',
    'homepage': 'https://cannabisdata.com',
    'logos': {
        'light': 'dashboard/images/logos/cannabis-data-logo.svg',
        'dark': 'dashboard/images/logos/cannabis-data-logo.svg',
        'favicon': 'images/logos/favicon.ico',
    },
    'policies': {
        'license': 'https://docs.cannlytics.com/about/license',
        'privacy': 'https://docs.cannlytics.com/about/privacy-policy',
        'security': 'https://docs.cannlytics.com/about/security-policy',
        'terms': 'https://docs.cannlytics.com/about/terms-of-service',
    },
}

#-----------------------------------------------------------------------
# Data models
#-----------------------------------------------------------------------

data_models = [
    {
        "label": "Dashboard",
        "url": "/",
        "icon": "grid",
        "key": "",
        "user_type": "*",
        "major": True,
        "hidden": True,
    },
    {
        "label": "Analytics",
        "url": "/analytics",
        "key": "analytics",
        "user_type": ["producer", "processor", "retailer", "consumer", "integrator"],
        "image_path": "",
        "description": "Explore rich analytics to better understand your choices and performance.",
        "separator": True
    },
    {
        "label": "Settings",
        "url": "/settings",
        "icon": "settings",
        "key": "settings",
        "user_type": "*",
        "major": True,
        "description": "Manage your user and organization settings.",
        "image_path": "",
    },
    {
        "label": "Help",
        "url": "/help",
        "icon": "help-circle",
        "key": "help",
        "user_type": "*",
        "major": True,
        "hidden": True,
    },
    {
        'label': 'Logs',
        'key': 'logs',
        'singular': 'log',
        'abbreviation': 'L',
        'id_schema': '[abbreviation]%y%m%d',
        'sortable': True,
        'filter': True,
        'hidden': True,
        "fields": [
            {"key": "created_at", "label": "Time", "type": "datetime", "class": "field-sm"},
            {"key": "log_id", "label": "Log ID", "disabled": True, "hidden": True},
            {"key": "action", "label": "Action"},
            {"key": "changes", "label": "Changes", "type": "textarea"},
            {"key": "user", "label": "User ID", "disabled": True},
            {"key": "user_email", "label": "User email", "disabled": True},
            {"key": "user_name", "label": "User name", "disabled": True},
            {"key": "user_photo_url", "label": "User photo", "disabled": True},
            {"key": "type", "label": "Type", "class": "field-sm", "disabled": True},
            {"key": "key", "label": "Key", "class": "field-sm", "disabled": True},
        ],
    },
    {
        'label': 'Files',
        'key': 'files',
        'singular': 'file',
        'abbreviation': 'F',
        'id_schema': '[abbreviation]%y%m%d',
        'sortable': True,
        'filter': True,
        'hidden': True,
        "fields": [
            {"key": "file_id", "label": "File ID", "disabled": True, "hidden": True},
            {"key": "name", "label": "Name", "disabled": True},
            {"key": "uploaded_at", "label": "Uploaded At", "type": "datetime", "disabled": True},
            {"key": "uploaded_by", "label": "Uploaded By", "disabled": True},
            {"key": "content_type", "label": "File Type", "disabled": True},
            {"key": "file_size", "label": "File Size", "disabled": True},
            {"key": "version", "label": "Version", "class": "field-sm", "disabled": True},
            {"key": "type", "label": "Type", "class": "field-sm", "disabled": True},
            {"key": "key", "label": "Key", "class": "field-sm", "disabled": True},
            {"key": "pinned", "label": "Pin File", "type": "bool", "onchange": "pinFile"},
        ],
    },
]

#-----------------------------------------------------------------------
# Page-specific material.
#-----------------------------------------------------------------------

material = {
    "settings": {
        "options": [
            {"title": "API", "url": "/settings/api"},
            {"title": "Organization settings", "url": "/settings/organizations"},
            {"title": "User Settings", "url": "/settings/user"},
            # Optional: Add additional settings.
            # {"title": "Data", "url": "/settings/data"},
            # {"title": "Logs", "url": "/settings/logs"},
            # {"title": "Notifications", "url": "/settings/notifications"},
            # {"title": "Theme", "url": "/settings/theme"},
        ],
        "organizations": {
            "breadcrumbs": [
                {"title": "Settings", "url": "settings"},
                {"title": "Organizations", "active": True},
            ],
            "fields": [
                {"key": "name", "label": "Name"},
                {"key": "trade_name", "label": "Trade Name"},
                {"key": "type", "label": "Type", "type": "select", "options": [{"key": "lab", "label": "Lab"}, {"key": "producer", "label": "Producer"}, {"key": "retailer", "label": "Retailer"}, {"key": "integrator", "label": "Integrator"},]},
                {"key": "website", "label": "Website"},
                {"type": "email", "key": "email", "label": "Email"},
                {"key": "phone", "label": "Phone"},
                {"key": "address", "label": "Address", "secondary": True},
                {"key": "city", "label": "City", "secondary": True},
                {"key": "state", "label": "State", "secondary": True},
                {"key": "country", "label": "Country", "secondary": True},
                {"key": "zip_code", "label": "Zip Code", "secondary": True},
                {"key": "external_id", "label": "External ID", "secondary": True},
            ],
            "placeholder": {
                "action": "Start an organization",
                "height": "200px",
                "image": "",
                "title": "Create or join an organization",
                "message": "Add team members to your organization or join an organization to begin collaborating.",
                "url": "/settings/organizations/new",
            },
        },
        "organization_breadcrumbs": [
            {"title": "Settings", "url": "/settings"},
            {"title": "Organization Settings", "active": True},
        ],
        "user_breadcrumbs": [
            {"title": "Settings", "url": "/settings"},
            {"title": "User Settings", "active": True},
        ],
        "user_fields": [
            {"key": "name", "label": "Name"},
            {"key": "position", "label": "Position"},
            {"type": "email", "key": "email", "label": "Email"},
            {"key": "phone_number", "label": "Phone"},
        ],
        "user_options": [
            {"title": "Change your password", "url": "/account/password-reset"},
        ],
    },
    "logs": {
        "placeholder": {
            "height": "200px",
            "image": "",
            "title": "No logs in this period",
            "message": "You can create a custom log for traceability or quality control purposes or try expanding your search.",
        },
        "fields": [
            {"key": "created_at", "label": "Time", "type": "datetime", "class": "field-sm"},
            {"key": "log_id", "label": "Log ID", "disabled": True, "hidden": True},
            {"key": "action", "label": "Action"},
            {"key": "changes", "label": "Changes", "type": "textarea"},
            {"key": "user", "label": "User ID", "disabled": True},
            {"key": "user_email", "label": "User email", "disabled": True},
            {"key": "user_name", "label": "User name", "disabled": True},
            {"key": "user_photo_url", "label": "User photo", "disabled": True},
            {"key": "type", "label": "Type", "class": "field-sm", "disabled": True},
            {"key": "key", "label": "Key", "class": "field-sm", "disabled": True},
        ],
    },
    "files": {
        "placeholder": {
            "height": "200px",
            "image": "",
            "title": "No logs in this period",
            "message": "You can create a custom log for traceability or quality control purposes or try expanding your search.",
        },
        "fields": [
            {"key": "file_id", "label": "File ID", "disabled": True, "hidden": True},
            {"key": "name", "label": "Name", "disabled": True},
            {"key": "uploaded_at", "label": "Uploaded At", "type": "datetime", "disabled": True},
            {"key": "uploaded_by", "label": "Uploaded By", "disabled": True},
            {"key": "content_type", "label": "File Type", "disabled": True},
            {"key": "file_size", "label": "File Size", "disabled": True},
            {"key": "version", "label": "Version", "class": "field-sm", "disabled": True},
            {"key": "type", "label": "Type", "class": "field-sm", "disabled": True},
            {"key": "key", "label": "Key", "class": "field-sm", "disabled": True},
            {"key": "pinned", "label": "Pin File", "type": "bool", "onchange": "pinFile"},
        ],
    },
}

#-----------------------------------------------------------------------
# Page-specific data loaded from Firestore.
#-----------------------------------------------------------------------

page_data = {
    "get-started": {
        "collections": [
            {
                "name": "verifications",
                "ref": "public/verifications/verification_data"
            }
        ]
    },
    # "support": {
    #     "documents": [
    #         {
    #             "name": "paypal",
    #             "ref": "credentials/paypal"
    #         }
    #     ]
    # },
}
