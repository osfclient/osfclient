import datetime
import json
import logging

import furl
import requests
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

from osfsync import settings
from osfsync.database import clear_models, Session
from osfsync.database import models
from osfsync.exceptions import AuthError, TwoFactorRequiredError

logger = logging.getLogger(__name__)


def get_current_user():
    """
    Fetch the database object representing the currently active user
    :return: A user object (raises exception if none found)
    :rtype: models.User
    :raises SQLAlchemyError
    """
    with Session() as session:
        return session.query(models.User).one()


class AuthClient(object):
    """Manages authorization flow """

    def _authenticate(self, username, password, *, otp=None):
        """ Tries to use standard auth to authenticate and create a personal access token through APIv2
            :param str or None otp: One time password used for two-factor authentication
            :return str: personal_access_token
            :raise AuthError or TwoFactorRequiredError
        """
        token_url = furl.furl(settings.API_BASE)
        token_url.path.add('/v2/tokens/')
        token_request_body = {
            'data': {
                'type': 'tokens',
                'attributes': {
                    'name': 'OSF-Sync - {}'.format(datetime.date.today()),
                    'scopes': settings.APPLICATION_SCOPES
                }
            }
        }
        headers = {
            'User-Agent': 'OSF Sync',
            'content-type': 'application/json'
        }

        if otp is not None:
            headers['X-OSF-OTP'] = otp

        try:
            resp = requests.post(
                token_url.url,
                headers=headers,
                data=json.dumps(token_request_body),
                auth=(username, password)
            )
        except Exception:
            # Invalid credentials probably, but it's difficult to tell
            # Regardless, will be prompted later with dialogbox later
            # TODO: narrow down possible exceptions here
            raise AuthError('Login failed')
        else:
            if resp.status_code in (401, 403):
                # If login failed because of a missing two-factor authentication code, notify the user to try again
                # This header appears for basic auth requests, and only when a valid password is provided
                otp_val = resp.headers.get('X-OSF-OTP', '')
                if otp_val.startswith('required'):
                    raise TwoFactorRequiredError('Must provide code for two-factor authentication')
                else:
                    raise AuthError('Invalid credentials')
            elif not resp.status_code == 201:
                raise AuthError('Invalid authorization response')
            else:
                json_resp = resp.json()
                return json_resp['data']['attributes']['token_id']

    def _create_user(self, username, personal_access_token):
        """ Tries to authenticate and create user.

        :return models.User: user
        :raise AuthError
        """
        logger.debug('User doesn\'t exist. Attempting to authenticate, then creating user.')

        user = models.User(
            id='',
            full_name='',
            login=username,
            oauth_token=personal_access_token,
        )
        return self.populate_user_data(user)

    def populate_user_data(self, user):
        """
        Takes a user object, makes a request to ensure auth is working,
        and fills in any missing user data.

        :return models.User: user
        :raise AuthError
        """
        me = furl.furl(settings.API_BASE)
        me.path.add('/v2/users/me/')
        header = {'Authorization': 'Bearer {}'.format(user.oauth_token)}
        try:
            # TODO: Update to use client/osf.py
            resp = requests.get(me.url, headers=header)
        except Exception:
            raise AuthError('Login failed. Please log in again.')
        else:
            if resp.status_code != 200:
                raise AuthError('Invalid credentials. Please log in again.')
            json_resp = resp.json()
            data = json_resp['data']

            user.id = data['id']
            user.full_name = data['attributes']['full_name']

            return user

    def login(self, *, username=None, password=None, otp=None):
        """
        Log in with the provided std auth credentials and return the database user object
        :param str username: The username / email address of the user
        :param str password: The password of the user
        :param str otp: One time password used for two-factor authentication
        :return models.User: A database object representing the logged-in user
        :raises: AuthError or TwoFactorRequiredError
        """
        if not username or not password:
            raise AuthError('Username and password required for login.')

        try:
            user = get_current_user()
        except NoResultFound:
            user = None

        personal_access_token = self._authenticate(username, password, otp=otp)
        if user:
            if user.login != username:
                # Different user authenticated, drop old user and allow login
                clear_models()
                user = self._create_user(username, personal_access_token)
            else:
                user.oauth_token = personal_access_token
        else:
            user = self._create_user(username, personal_access_token)

        try:
            with Session() as session:
                session.add(user)
                session.commit()
        except SQLAlchemyError:
            msg = 'Unable to save user data. Please try again later'
            logger.exception(msg)
            raise AuthError(msg)
        return user
