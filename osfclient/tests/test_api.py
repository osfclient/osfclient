from mock import call, patch
import pytest

from osfclient import OSF
from osfclient.exceptions import OSFException
from osfclient.models import OSFSession
from osfclient.models import OSFCore
from osfclient.models import Project

from osfclient.tests.fake_responses import project_node, registration_node, fake_node
from osfclient.tests.mocks import FakeResponse


@patch.object(OSFSession, 'basic_auth')
def test_basic_auth(session_basic_auth):
    OSF('joe@example.com', 'secret_password')
    session_basic_auth.assert_called_with('joe@example.com', 'secret_password')


@patch.object(OSFSession, 'token_auth')
def test_token_auth(session_token_auth):
    OSF(token='asdfg')
    session_token_auth.assert_called_with('asdfg')


@patch.object(OSFSession, 'basic_auth')
def test_login_username_password(session_basic_auth):
    osf = OSF()
    assert not session_basic_auth.called

    osf.login('joe@example.com', 'secret_password')
    session_basic_auth.assert_called_with('joe@example.com', 'secret_password')


@patch.object(OSFSession, 'token_auth')
def test_login_token(session_token_auth):
    osf = OSF()
    assert not session_token_auth.called

    osf.login(token="asdfg")
    session_token_auth.assert_called_with("asdfg")


@patch.object(OSFCore, '_get', return_value=FakeResponse(200, project_node))
def test_get_project(OSFCore_get):
    osf = OSF()
    project = osf.project('f3szh')

    calls = [call('https://api.osf.io/v2//guids/f3szh/'), call('https://api.osf.io/v2//nodes/f3szh/')]
    OSFCore_get.assert_has_calls(calls)
    assert isinstance(project, Project)


@patch.object(OSFCore, '_get', return_value=FakeResponse(200, registration_node))
def test_get_registration(OSFCore_get):
    osf = OSF()
    project = osf.project('f3szh')

    calls = [call('https://api.osf.io/v2//guids/f3szh/'), call('https://api.osf.io/v2//registrations/f3szh/')]
    OSFCore_get.assert_has_calls(calls)
    assert isinstance(project, Project)


@patch.object(OSFCore, '_get', return_value=FakeResponse(200, fake_node))
def test_get_fake(OSFCore_get):
    osf = OSF()
    with pytest.raises(OSFException) as exc:
        osf.project('f3szh')

    assert exc.value.args[0] == 'f3szh is unrecognized type fakes. Clone supports projects and registrations'
    OSFCore_get.assert_called_once_with(
        'https://api.osf.io/v2//guids/f3szh/'
        )


@patch.object(OSFCore, '_get', return_value=FakeResponse(404, project_node))
def test_failed_get_project(OSFCore_get):
    osf = OSF()
    with pytest.raises(RuntimeError):
        osf.project('f3szh')

    OSFCore_get.assert_called_once_with(
        'https://api.osf.io/v2//guids/f3szh/'
        )
