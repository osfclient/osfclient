from unittest.mock import MagicMock


def MockFile(name):
    mock = MagicMock(name='File-%s' % name, path=name)
    return mock


def MockStorage(name):
    mock = MagicMock(name='Storage-%s' % name,
                     files=[MockFile('a'), MockFile('b')])
    return mock


def MockProject(name):
    mock = MagicMock(name='Project-%s' % name,
                     storages=[MockStorage('osf'), MockStorage('gh')])
    return mock
