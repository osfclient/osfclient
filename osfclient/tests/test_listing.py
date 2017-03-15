"""Test `osf ls` command"""

from unittest.mock import patch, MagicMock, PropertyMock

from osfclient import filetree
from osfclient import list_


@patch('osfclient.osf.OSFClient')
@patch('osfclient.AuthClient')
def test_auth(MockAuthClient, MockOSFClient):
    args = MagicMock()
    username = PropertyMock(return_value=None)
    type(args).username = username

    node = MagicMock()
    path = PropertyMock(return_value='a')
    type(node).path = path

    node2 = MagicMock()
    path2 = PropertyMock(return_value='b')
    type(node2).path = path2

    filetree.get_project_files = MagicMock(return_value=[node, node2])

    list_(args)

    assert MockAuthClient.called
    username.assert_called_once_with()
    path.assert_called_once_with()
    path2.assert_called_once_with()
