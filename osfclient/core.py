from .session import OSFSession


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

    def _get(self, url):
        return self.session.get(url)

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
        """Extract JSON from response if `status_code` matches"""
        if response.status_code == status_code:
            return response.json()
        else:
            raise RuntimeError("Response has status "
                               "code {} not {}".format(response.status_code,
                                                       status_code))
