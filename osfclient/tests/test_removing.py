"""Test `osf remove` command"""

import pytest

from mock import call
from mock import patch

from osfclient import OSF
from osfclient.cli import remove

from osfclient.tests.mocks import MockArgs
from osfclient.tests.mocks import MockProject


def test_anonymous_doesnt_work():
    args = MockArgs(project='1234')

    with pytest.raises(SystemExit) as e:
        remove(args)

    expected = 'remove a file you need to provide a username and password'
    assert expected in e.value.args[0]


@patch.object(OSF, 'project', return_value=MockProject('1234'))
def test_remove_file(OSF_project):
    args = MockArgs(project='1234', username='joe', target='osfstorage/a/a/a')

    def simple_getenv(key):
        if key == 'OSF_PASSWORD':
            return 'secret'

    with patch('osfclient.cli.os.getenv', side_effect=simple_getenv):
        remove(args)

    OSF_project.assert_called_once_with('1234')

    MockProject = OSF_project.return_value
    MockStorage = MockProject._storage_mock.return_value
    for f in MockStorage.files:
        if f._path_mock.return_value == '/a/a/a':
            assert call.remove() in f.mock_calls


@patch.object(OSF, 'project', return_value=MockProject('1234'))
def test_wrong_storage_name(OSF_project):
    args = MockArgs(project='1234', username='joe', target='DOESNTEXIST/a/a/a')

    def simple_getenv(key):
        if key == 'OSF_PASSWORD':
            return 'secret'

    with patch('osfclient.cli.os.getenv', side_effect=simple_getenv):
        remove(args)

    OSF_project.assert_called_once_with('1234')

    # the mock storage is called osfstorage, so we should not call remove()
    MockProject = OSF_project.return_value
    MockStorage = MockProject._storage_mock.return_value
    for f in MockStorage.files:
        if f._path_mock.return_value == '/a/a/a':
            assert call.remove() not in f.mock_calls


@patch.object(OSF, 'project', return_value=MockProject('1234'))
def test_non_existant_file(OSF_project):
    args = MockArgs(project='1234', username='joe',
                    target='osfstorage/DOESNTEXIST/a')

    def simple_getenv(key):
        if key == 'OSF_PASSWORD':
            return 'secret'

    with patch('osfclient.cli.os.getenv', side_effect=simple_getenv):
        remove(args)

    OSF_project.assert_called_once_with('1234')

    # check that all files in osfstorage are visited but non get deleted
    MockProject = OSF_project.return_value
    MockStorage = MockProject._storage_mock.return_value
    for f in MockStorage.files:
        assert f._path_mock.called
        assert call.remove() not in f.mock_calls
