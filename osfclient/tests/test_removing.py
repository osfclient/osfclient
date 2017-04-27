"""Test `osf remove` command"""

import pytest

from unittest.mock import call
from unittest.mock import patch

from osfclient import OSF
from osfclient.cli import remove
from osfclient.models import Project

from osfclient.tests.mocks import MockArgs
from osfclient.tests.mocks import MockProject


def test_anonymous_doesnt_work():
    args = MockArgs()

    with pytest.raises(SystemExit):
        remove(args)


@patch.object(OSF, 'project', return_value=MockProject('1234'))
def test_remove_file(OSF_project):
    args = MockArgs(project='1234', username='joe', password='secret',
                    target='osfstorage/a/a/a')

    remove(args)

    OSF_project.assert_called_once_with('1234')

    MockProject = OSF_project.return_value
    MockStorage = MockProject._storage_mock.return_value
    for f in MockStorage.files:
        if f._path_mock.return_value == '/a/a/a':
            assert call.remove() in f.mock_calls


@patch.object(OSF, 'project', return_value=MockProject('1234'))
def test_wrong_storage_name(OSF_project):
    args = MockArgs(project='1234', username='joe', password='secret',
                    target='DOESNTEXIST/a/a/a')

    remove(args)

    OSF_project.assert_called_once_with('1234')

    # the mock storage is called osfstorage, so we should not call remove()
    MockProject = OSF_project.return_value
    MockStorage = MockProject._storage_mock.return_value
    for f in MockStorage.files:
        if f._path_mock.return_value == '/a/a/a':
            assert call.remove() not in f.mock_calls
