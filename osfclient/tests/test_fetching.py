"""Test `osf fetch` command."""

import os

from unittest import mock
from unittest.mock import patch, mock_open

from osfclient import OSF
from osfclient.cli import fetch

from osfclient.tests.mocks import MockProject
from osfclient.tests.mocks import MockArgs


@patch('osfclient.cli.os.makedirs')
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


@patch('osfclient.cli.os.makedirs')
@patch('osfclient.cli.os.path.exists', return_value=False)
@patch.object(OSF, 'project', return_value=MockProject('1234'))
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
    store = OSF_project.return_value.storages[0]
    assert store._name_mock.return_value == 'osfstorage'

    # should create a file in the same directory when no local
    # filename is specified
    assert mock.call('foobar.txt', 'wb') in mock_open_func.mock_calls
    assert not os_makedirs.called


@patch('osfclient.cli.os.makedirs')
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


@patch('osfclient.cli.os.path.exists', return_value=True)
@patch.object(OSF, 'project', return_value=MockProject('1234'))
def test_fetch_local_file_exists(OSF_project, os_path_exists, capsys):
    # check that `osf fetch` opens the right files with the right name
    # and mode when specifying a local filename
    args = MockArgs(project='1234', remote='osfstorage/a/a/a',
                    local='subdir/foobar.txt')

    return_value = fetch(args)
    assert return_value == 1
    out, err = capsys.readouterr()
    assert 'already exists, not overwriting' in out
