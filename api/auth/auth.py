"""
Authentication API
Copyright (c) 2022 Cannabis Data
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 1/22/2021
Updated: 11/22/2022
License: MIT License <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>

Description: Authentication mechanisms for the Cannlytics API, including API key
utility functions, request authentication and verification helpers,
and the authentication endpoints.
"""
# Standard imports.
from json import loads
from secrets import token_urlsafe

# External imports.
from datetime import datetime, timedelta
from django.http.response import JsonResponse

# Internal imports.
from cannlytics.auth.auth import authenticate_request, sha256_hmac
from cannlytics.firebase import (
    create_log,
    get_collection,
    get_document,
    update_document,
)

#-----------------------------------------------------------------------
# API Key Utilities
# FIXME: Insufficient permissions with desired design (data lives in 1 place)
# Current fix is to save key data to both the user's collection and the admin
# collection. It would be ideal to fix the Firestore security rules so
# data only needs to be stored in admin/api/api_key_hmacs
#-----------------------------------------------------------------------

def create_api_key(request, *args, **argv): #pylint: disable=unused-argument
    """Mint an API key for a user, granting programmatic use at the same
    level of permission as the user.
    Args:
        request (HTTPRequest): A request to get the user's session.
    Returns:
        (JsonResponse): A JSON response containing the API key in an
            `api_key` field.
    """
    user_claims = authenticate_request(request)
    uid = user_claims['uid']
    api_key = token_urlsafe(48)
    app_secret = get_document('admin/api')['app_secret_key']
    app_salt = get_document('admin/api')['app_salt']
    code = sha256_hmac(app_secret, api_key + app_salt)
    post_data = loads(request.body.decode('utf-8'))
    now = datetime.now()
    expiration_at = post_data['expiration_at']
    try:
        expiration_at = datetime.fromisoformat(expiration_at)
    except:
        expiration_at = datetime.strptime(expiration_at, '%m/%d/%Y')
    if expiration_at - now > timedelta(365):
        expiration_at = now + timedelta(365)
    key_data = {
        'created_at': now.isoformat(),
        'expiration_at': expiration_at.isoformat(),
        'name': post_data['name'],
        'permissions': post_data['permissions'],
        'uid': uid,
        'user_email': user_claims['email'],
        'user_name': user_claims.get('name', 'No Name'),
    }
    update_document(f'admin/api/api_key_hmacs/{code}', key_data)
    update_document(f'users/{uid}/api_key_hmacs/{code}', key_data)
    create_log(f'users/{uid}/logs', user_claims, 'Created API key.', 'api_key', 'api_key_create', [key_data])
    return JsonResponse({'status': 'success', 'api_key': api_key})


def delete_api_key(request, *args, **argv): #pylint: disable=unused-argument
    """Deletes a user's API key passed through an authorization header,
    e.g. `Authorization: API-key xyz`.
    Args:
        request (HTTPRequest): A request to get the user's API key.
    """
    user_claims = authenticate_request(request)
    uid = user_claims['uid']
    post_data = loads(request.body.decode('utf-8'))

    # FIXME: Get the name of the desired key to delete.

    # Delete the key from the users API keys.

    # Remove the key HMAC by created_at time.

    # authorization = request.META['HTTP_AUTHORIZATION']
    # api_key = authorization.split(' ')[-1]
    # app_secret = get_document('admin/api')['app_secret_key']
    # code = sha256_hmac(app_secret, api_key)
    # key_data = get_document(f'admin/api/api_key_hmacs/{code}')
    # uid = key_data['uid']
    # delete_document(f'admin/api/api_key_hmacs/{code}')
    # delete_document(f'users/{uid}/api_key_hmacs/{code}')
    # return JsonResponse({'status': 'success'})
    create_log(f'users/{uid}/logs', user_claims, 'Deleted API key.', 'api_key', 'api_key_delete', [{'deleted_at': datetime.now().isoformat()}])
    message = 'Delete API key not yet implemented, will be implemented shortly.'
    return JsonResponse({'error': True, 'message': message})


def get_api_key_hmacs(request, *args, **argv): #pylint: disable=unused-argument
    """Get a user's API key HMAC information.
    Args:
        request (HTTPRequest): A request to get the user's HMAC information.
    Returns:
        (JsonResponse): A JSON response containing the API key HMAC
            information in a `data` field.
    """
    user_claims = authenticate_request(request)
    uid = user_claims['uid']
    query = {'key': 'uid', 'operation': '==', 'value': uid}
    docs = get_collection('admin/api/api_key_hmacs', filters=[query])
    return JsonResponse({'status': 'success', 'data': docs})
