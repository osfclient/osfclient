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
