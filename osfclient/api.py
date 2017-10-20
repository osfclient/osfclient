from .exceptions import OSFException
from .models import OSFCore
from .models import Project


class OSF(OSFCore):
    """Interact with the Open Science Framework.

    This is the main point of contact for interactions with the
    OSF. Use the methods of this class to find projects, login
    to the OSF, etc.
    """
    def __init__(self, username=None, password=None, token=None):
        super(OSF, self).__init__({})
        if username is not None and password is not None:
            self.login(username, password)

    def login(self, username, password=None, token=None):
        """Login user for protected API calls."""
        self.session.basic_auth(username, password)

    def project(self, project_id):
        """Fetch project `project_id`."""
        type_ = self.guid(project_id)
        url = self._build_url(type_, project_id)
        if type_ in Project._types:
            return Project(self._json(self._get(url), 200), self.session)
        raise OSFException('{} is unrecognized type {}. Clone supports projects and registrations'.format(project_id, type_))

    def guid(self, guid):
        """Determines JSONAPI type for provided GUID"""
        return self._json(self._get(self._build_url('guids', guid)), 200)['data']['type']

    @property
    def username(self):
        if self.session.auth is not None:
            return self.session.auth[0]

    @property
    def password(self):
        if self.session.auth is not None:
            return self.session.auth[1]
