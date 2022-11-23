"""
Context Processors
Copyright (c) 2022 Cannabis Data
Copyright (c) 2021-2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 4/26/2021
Updated: 11/21/2022
License: MIT License <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>
"""
# External imports.
from dashboard.settings import (
    APP_VERSION_NUMBER,
    DEBUG,
    DEFAULT_FROM_EMAIL,
)

def selected_settings(request): #pylint: disable=unused-argument
    """Include relevant settings in a view's context."""
    return {
        'APP_VERSION_NUMBER': APP_VERSION_NUMBER,
        'CONTACT_EMAIL': DEFAULT_FROM_EMAIL,
        'DEBUG': DEBUG,
    }
