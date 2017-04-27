"""Test `osf upload` command"""

from unittest.mock import call
from unittest.mock import patch
from unittest.mock import mock_open

import pytest

from osfclient import OSF
from osfclient.cli import upload
from osfclient.models import Project

from osfclient.tests.mocks import MockArgs
from osfclient.tests.mocks import MockProject
from osfclient.tests.mocks import MockStorage


def test_anonymous_doesnt_work():
    args = MockArgs()

    with pytest.raises(SystemExit):
        upload(args)


@patch.object(OSF, 'project', return_value=MockProject('1234'))
@patch.object(Project, 'storage', return_value=MockStorage('osfstorage'))
def test_select_project(Project_storage, OSF_project):
    args = MockArgs(username='joe@example.com',
                    project='1234',
                    source='foo/bar.txt',
                    destination='bar/bar/foo.txt')

    def simple_getenv(key):
        if key == 'OSF_PASSWORD':
            return 'secret'

    fake_open = mock_open()

    with patch('osfclient.cli.open', fake_open):
        with patch('osfclient.cli.os.getenv', side_effect=simple_getenv):
            upload(args)

    assert call('foo/bar.txt', 'rb') in fake_open.mock_calls

    # the mock project created by calling OSF().project()
    fake_project = OSF_project.return_value
    expected = [call._storage_mock('osfstorage')]
    assert fake_project.mock_calls == expected

    expected = [call.create_file('bar/bar/foo.txt',
                                 fake_open.return_value)]
    # we should call the create_file method on the return
    # value of _storage_mock
    assert fake_project._storage_mock.return_value.mock_calls == expected
