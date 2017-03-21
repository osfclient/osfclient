from unittest.mock import MagicMock


def MockFile(name):
    mock = MagicMock(path=name)
    return mock


def MockStorage():
    mock = MagicMock(files=[MockFile('a'), MockFile('b')])
    return mock


def MockProject():
    mock = MagicMock(storages=[MockStorage(), MockStorage()])
    return mock
