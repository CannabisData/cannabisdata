"""
Get Value Given Key Filter
Copyright (c) 2022 Cannabis Data
Copyright (c) 2021-2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 12/16/2021
Updated: 11/21/2022
License: MIT License <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>
"""
from django.template.defaultfilters import register

@register.filter(name='dict_key')
def dict_key(data, key):
    """Returns the value for a given key from a dictionary."""
    value = data.get(key, '')
    if value is None:
        value = ''
    return value
