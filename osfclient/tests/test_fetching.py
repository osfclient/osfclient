"""Test `osf fetch` command."""

import os

from unittest import mock
from unittest.mock import patch, mock_open

from osfclient import OSF
from osfclient.cli import fetch

from osfclient.tests.mocks import MockProject
from osfclient.tests.mocks import MockArgs


@patch.object(OSF, 'project', return_value=MockProject('1234'))
def test_fetch_project(OSF_project):
    # check that `osf fetch` opens files with the right names and modes
    args = MockArgs(project='1234')

    mock_open_func = mock_open()

    with patch('osfclient.cli.open', mock_open_func):
        fetch(args)

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

            assert mock.call(full_path, 'wb') in mock_open_func.mock_calls
