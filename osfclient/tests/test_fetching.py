"""Test `osf fetch` command."""

import pytest

import mock
from mock import call, patch, mock_open

from osfclient import OSF
from osfclient.cli import fetch

from osfclient.tests.mocks import MockProject
from osfclient.tests.mocks import MockArgs


@patch('osfclient.cli.makedirs')
@patch('osfclient.cli.os.path.exists', return_value=False)
@patch.object(OSF, 'project', return_value=MockProject('1234'))
def test_fetch_file(OSF_project, os_path_exists, os_makedirs):
    # check that `osf fetch` opens the right files with the right name and mode
    args = MockArgs(project='1234', remote='osfstorage/a/a/a')

    mock_open_func = mock_open()

    with patch('osfclient.cli.open', mock_open_func):
        fetch(args)

    OSF_project.assert_called_once_with('1234')
    # check that the project and the files have been accessed
    store = OSF_project.return_value.storages[0]
    assert store._name_mock.return_value == 'osfstorage'

    # should create a file in the same directory when no local
    # filename is specified
    assert mock.call('a', 'wb') in mock_open_func.mock_calls


@patch('osfclient.cli.makedirs')
@patch('osfclient.cli.os.path.exists', return_value=False)
@patch('osfclient.cli.OSF.project', return_value=MockProject('1234'))
def test_fetch_file_local_name_specified(OSF_project, os_path_exists,
                                         os_makedirs):
    # check that `osf fetch` opens the right files with the right name
    # and mode when specifying a local filename
    args = MockArgs(project='1234', remote='osfstorage/a/a/a',
                    local='foobar.txt')

    mock_open_func = mock_open()

    with patch('osfclient.cli.open', mock_open_func):
        fetch(args)

    OSF_project.assert_called_once_with('1234')

    # check that the project and the files have been accessed
    project = OSF_project.return_value
    store = project._storage_mock.return_value
    assert store._name_mock.return_value == 'osfstorage'

    expected = [call._path_mock(), call.write_to(mock_open_func())]
    assert expected == store.files[0].mock_calls
    # second file should not have been looked at
    assert not store.files[1].mock_calls

    # should create a file in the same directory when no local
    # filename is specified
    assert mock.call('foobar.txt', 'wb') in mock_open_func.mock_calls
    assert not os_makedirs.called


@patch('osfclient.cli.makedirs')
@patch('osfclient.cli.os.path.exists', return_value=False)
@patch.object(OSF, 'project', return_value=MockProject('1234'))
def test_fetch_file_local_dir_specified(OSF_project, os_path_exists,
                                        os_makedirs):
    # check that `osf fetch` opens the right files with the right name
    # and mode when specifying a local filename
    args = MockArgs(project='1234', remote='osfstorage/a/a/a',
                    local='subdir/foobar.txt')

    mock_open_func = mock_open()

    with patch('osfclient.cli.open', mock_open_func):
        fetch(args)

    OSF_project.assert_called_once_with('1234')
    # check that the project and the files have been accessed
    store = OSF_project.return_value.storages[0]
    assert store._name_mock.return_value == 'osfstorage'

    assert (mock.call('subdir/foobar.txt', 'wb') in
            mock_open_func.mock_calls)
    assert mock.call('subdir', exist_ok=True) in os_makedirs.mock_calls


@patch.object(OSF, 'project', return_value=MockProject('1234'))
def test_fetch_local_file_exists(OSF_project):
    # check that `osf fetch` opens the right files with the right name
    # and mode when specifying a local filename
    args = MockArgs(project='1234', remote='osfstorage/a/a/a',
                    local='subdir/foobar.txt')

    def exists(path):
        if path == ".osfcli.config":
            return False
        else:
            return True

    with patch('osfclient.cli.os.path.exists', side_effect=exists):
        with pytest.raises(SystemExit) as e:
            fetch(args)

    assert 'already exists, not overwriting' in e.value.args[0]
