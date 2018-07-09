from mock import MagicMock, PropertyMock


# When using a PropertyMock store it as an attribute
# of the mock it belongs to so that later on a caller
# can assert whether or not it has been accessed
def MockFile(name):
    mock = MagicMock(name='File-%s' % name, path=name)
    path = PropertyMock(return_value=name)
    type(mock).path = path
    mock._path_mock = path
    hashes_dict = dict(md5='0' * 32, sha256='0' * 64)
    hashes = PropertyMock(return_value=hashes_dict)
    type(mock).hashes = hashes
    mock._hashes_mock = hashes
    return mock


def MockFolder(name):
    mock = MagicMock(name='Folder-%s' % name, path=name)
    path = PropertyMock(return_value=name)
    type(mock).path = path
    mock._path_mock = path
    name = PropertyMock(return_value=name)
    type(mock).name = name
    mock._name_mock = name
    return mock


def MockStorage(name):
    mock = MagicMock(name='Storage-%s' % name,
                     files=[MockFile('/a/a/a'), MockFile('b/b/b')])
    name = PropertyMock(return_value=name)
    type(mock).name = name
    mock._name_mock = name
    return mock


def MockProject(name):
    mock = MagicMock(name='Project-%s' % name,
                     storages=[MockStorage('osfstorage'), MockStorage('gh')])
    storage = MagicMock(name='Project-%s-storage' % name,
                        return_value=MockStorage('osfstorage'))
    type(mock).storage = storage
    mock._storage_mock = storage

    return mock


def MockArgs(username=None, password=None, output=None, project=None,
             source=None, destination=None, local=None, remote=None,
             target=None, force=False, update=False, recursive=False):
    args = MagicMock(spec=['username', 'password', 'output', 'project',
                           'source', 'destination', 'target', 'force',
                           'recursive'])
    args._username_mock = PropertyMock(return_value=username)
    type(args).username = args._username_mock
    args._password_mock = PropertyMock(return_value=password)
    type(args).password = args._password_mock

    args._output_mock = PropertyMock(return_value=output)
    type(args).output = args._output_mock
    args._project_mock = PropertyMock(return_value=project)
    type(args).project = args._project_mock

    args._source_mock = PropertyMock(return_value=source)
    type(args).source = args._source_mock
    args._destination_mock = PropertyMock(return_value=destination)
    type(args).destination = args._destination_mock

    args._target_mock = PropertyMock(return_value=target)
    type(args).target = args._target_mock

    args._remote_mock = PropertyMock(return_value=remote)
    type(args).remote = args._remote_mock
    args._local_mock = PropertyMock(return_value=local)
    type(args).local = args._local_mock

    args._force_mock = PropertyMock(return_value=force)
    type(args).force = args._force_mock
    args._update_mock = PropertyMock(return_value=update)
    type(args).update = args._update_mock

    args._recursive_mock = PropertyMock(return_value=recursive)
    type(args).recursive = args._recursive_mock

    return args


class FakeResponse:
    def __init__(self, status_code, json):
        self.status_code = status_code
        self._json = json

    def json(self):
        return self._json
