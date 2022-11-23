"""
Title Case Filter
Copyright (c) 2022 Cannabis Data
Copyright (c) 2021-2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 12/16/2021
Updated: 11/21/2022
License: MIT License <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>
"""
from django.template.defaultfilters import register

@register.filter(name='title_case')
def title_case(key):
    """Capitalize a string, removing underscores and hyphens."""
    return key.replace('_', ' ').replace('-', ' ').title()
