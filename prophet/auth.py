import os

from functools import wraps
from http import HTTPStatus

import msal
import requests

from jose import jwt
from flask import g, request

from prophet import app

TENANT_ID = os.environ.get('TENANT_ID')
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
API_AUDIENCE = os.environ.get('API_AUDIENCE')

AUTHORITY_BASE_URL = os.environ.get('AUTHORITY_BASE_URL')
AUTHORITY = f'{AUTHORITY_BASE_URL}/{TENANT_ID}'
ISSUER_BASE_URL = os.environ.get('ISSUER_BASE_URL')
ISSUER = f'{ISSUER_BASE_URL}/{TENANT_ID}/'

ALGORITHMS = ('RS256',)

msal_app = msal.ConfidentialClientApplication(
    CLIENT_ID, CLIENT_SECRET, AUTHORITY)


class AuthError(Exception):
    def __init__(self, description, status_code=HTTPStatus.UNAUTHORIZED):
        self.description = description
        self.status_code = status_code


@app.errorhandler(AuthError)
def handle_auth_error(e):
    return {
        'error': {
            'code': 'auth_error',
            'description': e.description,
        },
    }, e.status_code


def get_token_auth_header():
    """Extract the auth token from the HTTP Authorization header.
    """

    auth = request.headers.get('Authorization', None)
    if auth is None:
        raise AuthError("Authorization header not present")

    parts = auth.split()

    if parts[0].lower() != 'bearer' or len(parts) != 2:
        raise AuthError("Could not parse Authorization header")

    token = parts[1]
    return token


def requires_auth(f):
    """Decorator for making a route require an access token.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        # Fetch a list of valid RSA keys from the AUTHORITY server
        # TODO Cache this list (Cache-Control header on it is
        # "private, max-age=86400")
        jwks_resp = requests.get(f'{AUTHORITY}/discovery/v2.0/keys')
        jwks = jwks_resp.json()

        unverified_header = jwt.get_unverified_header(token)
        if unverified_header['alg'] not in ALGORITHMS:
            raise AuthError(
                f"{unverified_header['alg']} algorithm not suppored")

        # Look for a matching RSA key in the keys from the AUTHORITY server
        rsa_key = None
        for key in jwks['keys']:
            if key['kid'] == unverified_header['kid']:
                # Copy over needed parts
                # TODO Can/should a full copy be made?
                rsa_key = {k: key[k] for k in ('kty', 'kid', 'use', 'n', 'e')}
                break

        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_AUDIENCE,
                    issuer=ISSUER)
            except jwt.ExpiredSignatureError:
                raise AuthError("JWT token expired")
            except jwt.JWTClaimsError as e:
                raise AuthError(str(e))
            except Exception as e:
                raise AuthError(str(e))

            g.user_access_token = token
            g.current_user = payload
            return f(*args, **kwargs)
        else:
            raise AuthError("Token key not found")

    return decorated


def requires_scopes(scopes):
    """Decorator for requiring a user to have a scope to access an endpoint.

    This must be applied after `requires_auth()` in order to work.
    """
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(g, 'current_user'):
                raise AuthError("Sign in required")

            user_scopes = g.current_user.get('scp', '').split()
            for s in scopes:
                if s not in user_scopes:
                    raise AuthError(f"Scope `{s}` required")

            return f(*args, **kwargs)

        return decorated

    return wrapper


def user_has_scope(scopes):
    """Determines if the scope is present in the access token.
    """

    if not hasattr(g, 'current_user'):
        return False

    user_scopes = g.current_user.get('scp', '').split()
    return all(s in user_scopes for s in scopes)
