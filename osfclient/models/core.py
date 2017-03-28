import numbers

from .session import OSFSession


class OSFException(Exception):
    pass


class UnauthorizedException(OSFException):
    pass


class FolderExistsException(OSFException):
    def __init__(self, name):
        self.args = ('Folder %s already exists.' % name,)


# Base class for all models and the user facing API object
class OSFCore:
    def __init__(self, json, session=None):
        if session is None:
            self.session = OSFSession()
        else:
            self.session = session

        self._update_attributes(json)

    def _update_attributes(self, json):
        pass

    def _build_url(self, *args):
        return self.session.build_url(*args)

    def _get(self, url, *args, **kwargs):
        response = self.session.get(url, *args, **kwargs)
        if response.status_code == 401:
            raise UnauthorizedException()

        return response

    def _put(self, url, *args, **kwargs):
        response = self.session.put(url, *args, **kwargs)
        if response.status_code == 401:
            raise UnauthorizedException()

        return response

    def _get_attribute(self, json, *keys, default=None):
        # pick value out of a (nested) dictionary
        # `keys` is a list of keys
        # XXX what should happen if a key doesn't match half way down
        # XXX traversing the list of keys?
        value = json
        try:
            for key in keys:
                value = value[key]

        except KeyError:
            if default is not None:
                return default
            else:
                raise

        return value

    def _json(self, response, status_code):
        """Extract JSON from response if `status_code` matches."""
        if isinstance(status_code, numbers.Integral):
            status_code = (status_code,)

        if response.status_code in status_code:
            return response.json()
        else:
            raise RuntimeError("Response has status "
                               "code {} not {}".format(response.status_code,
                                                       status_code))

    def _follow_next(self, url):
        """Follow the 'next' link on paginated results."""
        response = self._json(self._get(url), 200)
        data = response['data']

        next_url = self._get_attribute(response, 'links', 'next')
        while next_url is not None:
            response = self._json(self._get(next_url), 200)
            data.extend(response['data'])
            next_url = self._get_attribute(response, 'links', 'next')

        return data
