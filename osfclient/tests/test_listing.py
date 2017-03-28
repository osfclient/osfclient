"""Test `osf ls` command"""

from unittest.mock import patch, MagicMock, PropertyMock, mock_open

from osfclient import OSF
from osfclient.cli import list_

from osfclient.tests.mocks import MockProject
from osfclient.tests.mocks import MockArgs


@patch('osfclient.cli.OSF')
def test_anonymous_doesnt_use_password(MockOSF):
    args = MockArgs()

    list_(args)

    MockOSF.assert_called_once_with(username=None, password=None)


@patch('osfclient.cli.OSF')
def test_username_password(MockOSF):
    args = MockArgs(username='joe@example.com')

    def simple_getenv(key):
        if key == 'OSF_PASSWORD':
            return 'secret'

    with patch('osfclient.cli.os.getenv',
               side_effect=simple_getenv) as mock_getenv:
        list_(args)

    MockOSF.assert_called_once_with(username='joe@example.com',
                                    password='secret')
    mock_getenv.assert_called_with('OSF_PASSWORD')


@patch.object(OSF, 'project', return_value=MockProject('1234'))
def test_get_project(OSF_project):
    args = MockArgs(project='1234')

    list_(args)

    OSF_project.assert_called_once_with('1234')
    # check that the project and the files have been printed
    for store in OSF_project.return_value.storages:
        assert store._name_mock.called
        for f in store.files:
            assert f._path_mock.called
