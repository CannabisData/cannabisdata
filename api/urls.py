"""
API URLs
Copyright (c) 2022 Cannabis Data
Copyright (c) 2021-2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 4/21/2021
Updated: 11/22/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API URLs to interface with cannabis data and analytics.
"""
# External imports.
from django.urls import include, path
from rest_framework import urlpatterns #pylint: disable=unused-import

# Core API imports.
from api.auth import auth
from api.base import base

# Functional API imports.
from api.data import data, license_data
from api.stats import stats

# Administrative API imports.
from api.organizations import organizations
from api.users import users
from api.settings import settings


app_name = 'api' # pylint: disable=invalid-name

urlpatterns = [

    # Base API endpoint for users to discover an index of endpoints.
    path('', base.index, name='index'),

    # Authentication API endpoints.
    path('auth', include([
        path('/create-key', auth.create_api_key),
        path('/delete-key', auth.delete_api_key),
        path('/get-keys', auth.get_api_key_hmacs),
    ])),

    # Data API endpoints.
    path('data', include([

        # Base data API endpoint for users to find available datasets.
        path('', data.data_base),

        # License data.
        path('/licenses', include([
            path('', license_data.license_data),
            path('/<license_number>', license_data.license_data),
        ])),

        # CCRS data endpoints.
        # FIXME: Re-design CCRS endpoints around timeseries statistics.
        # path('/ccrs/areas', ccrs_data.areas),
        # path('/ccrs/contacts', ccrs_data.contacts),
        # path('/ccrs/integrators', ccrs_data.integrators),
        # path('/ccrs/inventory', ccrs_data.inventory),
        # path('/ccrs/inventory_adjustments', ccrs_data.inventory_adjustments),
        # path('/ccrs/plants', ccrs_data.plants),
        # path('/ccrs/plant_destructions', ccrs_data.plant_destructions),
        # path('/ccrs/products', ccrs_data.products),
        # path('/ccrs/lab_results', ccrs_data.lab_results),
        # path('/ccrs/licensees', ccrs_data.licensees),
        # path('/ccrs/sale_headers', ccrs_data.sale_headers),
        # path('/ccrs/sale_details', ccrs_data.sale_details),
        # path('/ccrs/strains', ccrs_data.strains),
        # path('/ccrs/transfers', ccrs_data.transfers),

    ])),

    # Stats endpoints.
    path('stats', include([

        path('', stats.stats_base),

        # TODO: Market basket analysis.

        # TODO: Impulse response functions / forecasting.

    ])),

    # Organization API endpoints.
    path('organizations', include([
        path('/<organization_id>', organizations.organizations),
        path('/<organization_id>/settings', organizations.organizations),
        path('/<organization_id>/team', organizations.organization_team),
        path('/<organization_id>/team/<user_id>', organizations.organization_team),
        path('/<organization_id>/join', organizations.join_organization),
    ])),

    # User API Endpoints
    path('users', include([
        path('', users.users),
        path('/<user_id>', users.users),
        path('/<user_id>/about', users.users),
        path('/<user_id>/consumption', users.users),
        path('/<user_id>/spending', users.users),
        path('/<user_id>/logs', include([
            path('', settings.logs),
            path('/<log_id>', settings.logs),
        ])),
        path('/<user_id>/settings', users.users),
    ])),
]
