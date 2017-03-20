from unittest.mock import patch
import pytest

from osfclient.api import OSF
from osfclient.api import OSFCore
from osfclient.api import OSFSession


class FakeResponse:
    def __init__(self, status_code, json):
        self.status_code = status_code
        self._json = json

    def json(self):
        return self._json


@patch.object(OSFSession, 'basic_auth')
def test_basic_auth(session_basic_auth):
    OSF('joe@example.com', 'secret_password')
    session_basic_auth.assert_called_with('joe@example.com', 'secret_password')


@patch.object(OSFSession, 'basic_auth')
def test_login(session_basic_auth):
    osf = OSF()
    assert not session_basic_auth.called

    osf.login('joe@example.com', 'secret_password')
    session_basic_auth.assert_called_with('joe@example.com', 'secret_password')


@patch.object(OSFCore, '_get', return_value=FakeResponse(200, '{"data": 123}'))
def test_get_project(OSFCore_get):
    osf = OSF()
    project = osf.project('1234projectid')

    OSFCore_get.assert_called_once_with(
        'https://api.osf.io/v2//nodes/1234projectid/'
        )
    assert 'data' in project


@patch.object(OSFCore, '_get', return_value=FakeResponse(404, '{"data": 123}'))
def test_failed_get_project(OSFCore_get):
    osf = OSF()
    with pytest.raises(RuntimeError):
        osf.project('1234projectid')

    OSFCore_get.assert_called_once_with(
        'https://api.osf.io/v2//nodes/1234projectid/'
        )
