from unittest.mock import MagicMock, PropertyMock


# When using a PropertyMock store it as an attribute
# of the mock it belongs to so that later on a caller
# can assert whether or not it has been accessed
def MockFile(name):
    mock = MagicMock(name='File-%s' % name, path=name)
    path = PropertyMock(return_value=name)
    type(mock).path = path
    mock._path_mock = path
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
                     storages=[MockStorage('osf'), MockStorage('gh')])
    return mock


def MockArgs(username=None, password=None, output=None, project=None):
    args = MagicMock()
    args._username_mock = PropertyMock(return_value=username)
    type(args).username = args._username_mock
    args._password_mock = PropertyMock(return_value=password)
    type(args).output = args._password_mock

    args._output_mock = PropertyMock(return_value=output)
    type(args).output = args._output_mock
    args._project_mock = PropertyMock(return_value=project)
    type(args).project = args._project_mock

    return args


class FakeResponse:
    def __init__(self, status_code, json):
        self.status_code = status_code
        self._json = json

    def json(self):
        return self._json
