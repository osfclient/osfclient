"""Test `osf upload` command"""

from mock import call
from mock import patch
from mock import mock_open

import pytest

from osfclient import OSF
from osfclient.cli import upload
from osfclient.models import Project

from osfclient.tests.mocks import MockArgs
from osfclient.tests.mocks import MockProject
from osfclient.tests.mocks import MockStorage


def test_anonymous_doesnt_work():
    args = MockArgs(project='1234')

    with pytest.raises(SystemExit) as e:
        upload(args)

    expected = 'upload a file you need to provide a username and password'
    assert expected in e.value.args[0]


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
    expected = [call('osfstorage')]
    assert fake_project._storage_mock.mock_calls == expected
    # assert fake_project.mock_calls == expected

    expected = [call.create_file('bar/bar/foo.txt',
                                 fake_open.return_value, update=False)]
    # we should call the create_file method on the return
    # value of _storage_mock
    assert fake_project._storage_mock.return_value.mock_calls == expected


@patch.object(OSF, 'project', return_value=MockProject('1234'))
@patch.object(Project, 'storage', return_value=MockStorage('osfstorage'))
def test_recursive_requires_directory(Project_storage, OSF_project):
    # test that we check if source is a directory when using recursive mode
    args = MockArgs(username='joe@example.com',
                    project='1234',
                    source='foo/bar.txt',
                    recursive=True,
                    destination='bar/bar/foo.txt')

    def simple_getenv(key):
        if key == 'OSF_PASSWORD':
            return 'secret'

    with pytest.raises(RuntimeError) as e:
        with patch('osfclient.cli.os.getenv', side_effect=simple_getenv):
            with patch('osfclient.cli.os.path.isdir', return_value=False):
                upload(args)

    assert 'recursive' in str(e.value)
    assert 'Expected source (foo/bar.txt)' in str(e.value)
