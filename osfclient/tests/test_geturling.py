"""Test `osf geturl` command."""

import pytest

from io import StringIO
from mock import patch

from osfclient import OSF
from osfclient.cli import geturl
from osfclient.models import Storage

from osfclient.tests.mocks import MockArgs
from osfclient.tests.mocks import MockProject


@patch('sys.stdout', new_callable=StringIO)
@patch.object(OSF, 'project', return_value=MockProject('1234'))
def test_geturl(OSF_project, mock_stdout):
    # check that `osf geturl` opens the right files with the right name and mode
    args = MockArgs(project='1234', remote='osfstorage/a/a/a')

    geturl(args)

    OSF_project.assert_called_once_with('1234')
    # check that the project and the files have been accessed
    store = OSF_project.return_value.storages[0]
    assert store._name_mock.return_value == 'osfstorage'

    assert 'https://example.com' in mock_stdout.getvalue()
