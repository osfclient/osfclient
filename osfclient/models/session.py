import requests

from ..exceptions import UnauthorizedException


class OSFSession(requests.Session):
    auth = None
    __attrs__ = requests.Session.__attrs__ + ['base_url']

    def __init__(self):
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
            'User-Agent': 'osfclient v0.0.1',
            })
        self.base_url = 'https://api.osf.io/v2/'

    def basic_auth(self, username, password):
        self.auth = (username, password)
        if 'Authorization' in self.headers:
            self.headers.pop('Authorization')

    def build_url(self, *args):
        parts = [self.base_url]
        parts.extend(args)
        # canonical OSF URLs end with a slash
        return '/'.join(parts) + '/'

    def put(self, url, *args, **kwargs):
        response = super(OSFSession, self).put(url, *args, **kwargs)
        if response.status_code == 401:
            raise UnauthorizedException()
        return response

    def get(self, url, *args, **kwargs):
        response = super(OSFSession, self).get(url, *args, **kwargs)
        if response.status_code == 401:
            raise UnauthorizedException()
        return response
