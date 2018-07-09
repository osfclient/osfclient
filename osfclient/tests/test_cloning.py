"""Test `osf clone` command."""

import os

from mock import patch, mock_open, call

from osfclient import OSF
from osfclient.cli import clone

from osfclient.tests.mocks import MockProject
from osfclient.tests.mocks import MockArgs


@patch.object(OSF, 'project', return_value=MockProject('1234'))
def test_clone_project(OSF_project):
    # check that `osf clone` opens files with the right names and modes
    args = MockArgs(project='1234')

    mock_open_func = mock_open()

    with patch('osfclient.cli.open', mock_open_func):
        with patch('osfclient.cli.makedirs'):
            with patch('osfclient.cli.os.getenv', side_effect='SECRET'):
                clone(args)

    OSF_project.assert_called_once_with('1234')
    # check that the project and the files have been accessed
    for store in OSF_project.return_value.storages:
        assert store._name_mock.called

        for f in store.files:
            assert f._path_mock.called
            fname = f._path_mock.return_value
            if fname.startswith('/'):
                fname = fname[1:]

            full_path = os.path.join('1234',
                                     store._name_mock.return_value,
                                     fname)

            assert call(full_path, 'wb') in mock_open_func.mock_calls


@patch('osfclient.cli.checksum', return_value = '0' * 32)
@patch.object(OSF, 'project', return_value=MockProject('1234'))
def test_clone_project_update_file_exists_and_matches(OSF_project, checksum):
    # check that `osf clone --update` downloads all files except for any that
    # already exist locally and match the corresponding remote file
    args = MockArgs(project='1234', update=True)

    mock_open_func = mock_open()

    def exists(file_path):
        if file_path == '1234/osfstorage/a/a/a':
            return True
        else:
            return False

    with patch('osfclient.cli.open', mock_open_func):
        with patch('osfclient.cli.makedirs'):
            with patch('osfclient.cli.os.getenv', side_effect='SECRET'):
                with patch('osfclient.cli.os.path.exists', side_effect=exists):
                    clone(args)

    OSF_project.assert_called_once_with('1234')
    # check that the project and the files have been accessed
    for store in OSF_project.return_value.storages:
        assert store._name_mock.called

        for f in store.files:
            assert f._path_mock.called
            fname = f._path_mock.return_value
            if fname.startswith('/'):
                fname = fname[1:]

            full_path = os.path.join('1234',
                                     store._name_mock.return_value,
                                     fname)

            if full_path == '1234/osfstorage/a/a/a':
                assert call(full_path, 'wb') not in mock_open_func.mock_calls
            else:
                assert call(full_path, 'wb') in mock_open_func.mock_calls


@patch('osfclient.cli.checksum', return_value = '1' * 32)
@patch.object(OSF, 'project', return_value=MockProject('1234'))
def test_clone_project_update_file_exists_and_differs(OSF_project, checksum):
    # check that `osf clone --update` downloads all files and overwrites
    # existing files if they differ from the remote
    args = MockArgs(project='1234', update=True)

    mock_open_func = mock_open()

    def exists(file_path):
        if file_path == '1234/osfstorage/a/a/a':
            return True
        else:
            return False

    with patch('osfclient.cli.open', mock_open_func):
        with patch('osfclient.cli.makedirs'):
            with patch('osfclient.cli.os.getenv', side_effect='SECRET'):
                with patch('osfclient.cli.os.path.exists', side_effect=exists):
                    clone(args)

    OSF_project.assert_called_once_with('1234')
    # check that the project and the files have been accessed
    for store in OSF_project.return_value.storages:
        assert store._name_mock.called

        for f in store.files:
            assert f._path_mock.called
            fname = f._path_mock.return_value
            if fname.startswith('/'):
                fname = fname[1:]

            full_path = os.path.join('1234',
                                     store._name_mock.return_value,
                                     fname)

            assert call(full_path, 'wb') in mock_open_func.mock_calls
