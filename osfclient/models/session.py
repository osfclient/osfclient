import logging
import os
import time
import functools
import requests

from ..exceptions import UnauthorizedException
from ..__version__ import __version__


def _rate_limit(func=None, per_second=1):
    """Limit number of requests made per second.

    Will sleep for 1/``per_second`` seconds if the last request was
    made too recently.
    """
    if not func:
        return functools.partial(_rate_limit, per_second=per_second)

    @functools.wraps(func)
    def wrapper(self, url, *args, **kwargs):
        if self.last_request is not None:
            now = time.time()
            delta = now - self.last_request
            if delta < (1 / per_second):
                time.sleep(1 - delta)

        self.last_request = time.time()
        return func(self, url, *args, **kwargs)

    return wrapper


class OSFSession(requests.Session):
    auth = None
    __attrs__ = requests.Session.__attrs__ + ['base_url']

    def __init__(self, address=None):
        """Handle HTTP session related work."""
        super(OSFSession, self).__init__()
        self.headers.update({
            # Only accept JSON responses
            'Accept': 'application/vnd.api+json',
            # Only accept UTF-8 encoded data
            'Accept-Charset': 'utf-8',
            # Always send JSON
            'Content-Type': "application/json",
            # Custom User-Agent string
            'User-Agent': 'osfclient v' + __version__,
        })

        self.proxies.update({
            'http': os.getenv("HTTP_PROXY") or os.getenv("http_proxy"),
            'https': os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
        })
        self.base_url = address or 'https://api.osf.io/v2'
        self.last_request = None
        self.token = None

    def basic_auth(self, username, password):
        self.auth = (username, password)
        if 'Authorization' in self.headers:
            self.headers.pop('Authorization')

    def token_auth(self, token):
        self.token = token
        self.headers['Authorization'] = "Bearer %s" % token

    def build_url(self, *args):
        parts = [self.base_url]
        parts.extend(args)
        # canonical OSF URLs end with a slash
        return '/'.join(parts) + '/'

    @_rate_limit
    def put(self, url, *args, **kwargs):
        logging.getLogger().error(
            f"osf call: url: {url}, args: {args}, kwargs: {kwargs}")

        response = super(OSFSession, self).put(url, *args, **kwargs, timeout=6.10)
        if response.status_code == 401:
            raise UnauthorizedException()
        return response

    @_rate_limit(per_second=7)
    def get(self, url, *args, **kwargs):
        logging.getLogger().error(
            f"osf call: url: {url}, args: {args}, kwargs: {kwargs}")
        response = super(OSFSession, self).get(url, *args, **kwargs, timeout=6.10)
        if response.status_code == 401:
            raise UnauthorizedException()
        return response

    def patch(self, url, *args, **kwargs):
        logging.getLogger().error(
            f"osf call: url: {url}, args: {args}, kwargs: {kwargs}")
        response = super(OSFSession, self).patch(
            url, *args, **kwargs, timeout=6.10)
        if response.status_code == 401:
            raise UnauthorizedException()
        return response
