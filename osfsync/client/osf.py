"""APIv2 client library for interacting with the OSF API"""

import abc
import iso8601
import threading

import requests

from osfsync import settings
from osfsync.utils import Singleton
from osfsync.utils.authentication import get_current_user


class ClientLoadError(Exception):
    def __init__(self, *args, resource=None, status=None, errors=None):
        super(ClientLoadError, self).__init__(*args)
        self.resource = resource
        self.status = status
        self.errors = errors


class OSFClient(metaclass=Singleton):
    def __init__(self, *, limit=5):
        self.user = get_current_user()
        self.headers = {
            'User-Agent': 'OSF Sync',
            'Authorization': 'Bearer {}'.format(self.user.oauth_token),
        }
        self.throttler = threading.Semaphore(limit)  # TODO: Is throttling active?
        self.request_session = requests.Session()
        self.request_session.headers.update(self.headers)

    def get_node(self, id):
        return Node.load(self.request_session, id)

    def get_user(self, *, id='me'):
        return User.load(self.request_session, id=id)

    def request(self, *args, **kwargs):
        return self.request_session.request(*args, **kwargs)

    def stop(self):
        del type(self.__class__)._instances[self.__class__]


class BaseResource(abc.ABC):
    OSF_HOST = settings.API_BASE
    API_PREFIX = settings.API_VERSION
    BASE_URL = '{}/{}'.format(OSF_HOST, API_PREFIX)

    def __init__(self, request_session, data):
        self.request_session = request_session
        self.id = data['id']
        self.type = data['type']
        self.raw = data
        for attribute, value in data['attributes'].items():
            setattr(self, attribute, value)

    @classmethod
    def get_url(cls, *args, **kwargs):
        return cls.BASE_URL

    @classmethod
    def from_data(cls, request_session, data):
        return cls(request_session, data)

    @classmethod
    def load(cls, request_session, *args, **kwargs):
        resp = request_session.get(
            cls.get_url(*args, **kwargs),
            params={'page[size]': 250},
            timeout=(settings.CONNECT_TIMEOUT, settings.READ_TIMEOUT),
        )
        if resp.status_code >= 500:
            raise ClientLoadError(
                resource=cls.RESOURCE,
                status=resp.status_code,
                errors=['Server error']
            )
        data = resp.json()

        if 'errors' in data:
            raise ClientLoadError(
                resource=cls.RESOURCE,
                status=resp.status_code,
                errors=data['errors']
            )

        if isinstance(data['data'], list):
            l = data['data']
            while data['links'].get('next'):
                resp = request_session.get(
                    data['links']['next'],
                    params={'page[size]': 250},
                    timeout=(settings.CONNECT_TIMEOUT, settings.READ_TIMEOUT),
                )
                data = resp.json()
                l.extend(data['data'])
            return [cls.from_data(request_session, item) for item in l]
        return cls.from_data(request_session, data['data'])

    def _fetch_related(self, relationship, data):
        items = data['data']
        for item in items:
            yield item
        if data['links'].get('next'):
            for item in self.fetch_related(
                    relationship,
                    next_url=data['links']['next']
            ):
                yield item

    def fetch_related(self, relationship, *, query=None, next_url=None):
        relation = self.raw['relationships'].get(relationship)
        if not relation:
            return None

        url = next_url or self.raw['relationships'][relationship]['links']['related']['href']
        params = {'page[size]': 250}
        params.update(query or {})
        resp = self.request_session.get(
            url,
            params=params,
            timeout=(settings.CONNECT_TIMEOUT, settings.READ_TIMEOUT),
        )
        data = resp.json()
        items = data['data']
        if not isinstance(items, list):
            return items
        else:
            return self._fetch_related(relationship, data)


class User(BaseResource):
    """Fetch API data relevant to a specific user"""
    RESOURCE = 'users'

    @classmethod
    def get_url(cls, *, id='me'):
        return '{}/{}/{}/'.format(cls.BASE_URL, cls.RESOURCE, id)

    def get_nodes(self):
        return UserNode.load(self.request_session, self.id)


class Node(BaseResource):
    """Fetch API data relevant to a specific Node"""
    RESOURCE = 'nodes'

    def __init__(self, request_session, data):
        super().__init__(request_session, data)
        self.date_created = iso8601.parse_date(self.date_created)
        self.date_modified = iso8601.parse_date(self.date_modified)

        if 'embeds' in data and data['embeds']['parent'].get('data'):
            self.parent = Node(request_session, data['embeds']['parent']['data'])
        else:
            self.parent = None

    @classmethod
    def get_url(cls, id):
        return '{}/{}/{}/?embed=parent'.format(cls.BASE_URL, cls.RESOURCE, id)

    def get_storage(self, *, id='osfstorage'):
        # TODO: At present only osfstorage is fully supported for syncing
        return next(
            storage
            for storage in NodeStorage.load(self.request_session, self.id)
            if storage.provider == id
        )

    def get_children(self, *, lazy=False):
        related = map(
            lambda data: Node(self.request_session, data),
            self.fetch_related('children', query={'embed': 'parent'})
        )
        if lazy:
            return related
        else:
            return list(related)


class UserNode(Node):
    """Fetch API data about nodes owned by a specific user"""

    @classmethod
    def get_url(cls, id):
        return '{}/users/{}/nodes/'.format(cls.BASE_URL, id)


class StorageObject(BaseResource):
    """Represent API data for files or folders under a specific node"""

    def __init__(self, request_session, data, *, parent=None):
        super().__init__(request_session, data)
        self.parent = parent
        if hasattr(self, 'date_modified') and self.date_modified:
            self.date_modified = iso8601.parse_date(self.date_modified)
        if hasattr(self, 'last_touched') and self.last_touched:
            self.last_touched = iso8601.parse_date(self.last_touched)

    @classmethod
    def get_url(cls, id):
        return '{}/files/{}/'.format(cls.BASE_URL, id)

    @classmethod
    def load(cls, request_session, *args):
        resp = request_session.get(
            cls.get_url(*args),
            params={'page[size]': 250},
            timeout=(settings.CONNECT_TIMEOUT, settings.READ_TIMEOUT),
        )
        data = resp.json()

        if 'errors' in data:
            raise ClientLoadError(
                resource=cls.RESOURCE,
                status=resp.status_code,
                errors=data['errors']
            )

        if isinstance(data['data'], list):
            return [
                (Folder if item['attributes']['kind'] == 'folder' else File)(request_session, item)
                for item in data['data']
            ]
        return cls(request_session, data['data'])


class Folder(StorageObject):
    """Represent API data for folders under a specific node"""
    is_dir = True

    def __repr__(self):
        return '<{0} {1} name={2} path={2}>'.format(self.__class__.__name__, id(self), self.name, self.path)

    def get_children(self, *, lazy=False):
        related = map(
            lambda item: (Folder if item['attributes']['kind'] == 'folder' else File)(self.request_session, item, parent=self),
            self.fetch_related('files')
        )
        if lazy:
            return related
        else:
            return list(related)


class NodeStorage(Folder):
    """Fetch API list of storage options under a node"""

    @classmethod
    def get_url(cls, node_id):
        return '{}/{}/{}/files/'.format(
            cls.BASE_URL,
            Node.RESOURCE,
            node_id
        )


class File(StorageObject):
    """Represent API data for files under a specific node"""
    is_dir = False

    def __repr__(self):
        return '<RemoteFile({}, {}, {}, {}>'.format(self.id, self.name, self.kind, self.parent.id)
