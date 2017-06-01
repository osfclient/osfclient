from mock import patch
import pytest

from osfclient import OSF
from osfclient.models import OSFSession
from osfclient.models import OSFCore
from osfclient.models import Project

from osfclient.tests.fake_responses import project_node
from osfclient.tests.mocks import FakeResponse


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


@patch.object(OSFCore, '_get', return_value=FakeResponse(200, project_node))
def test_get_project(OSFCore_get):
    osf = OSF()
    project = osf.project('f3szh')

    OSFCore_get.assert_called_once_with(
        'https://api.osf.io/v2//nodes/f3szh/'
        )
    assert isinstance(project, Project)


@patch.object(OSFCore, '_get', return_value=FakeResponse(404, project_node))
def test_failed_get_project(OSFCore_get):
    osf = OSF()
    with pytest.raises(RuntimeError):
        osf.project('f3szh')

    OSFCore_get.assert_called_once_with(
        'https://api.osf.io/v2//nodes/f3szh/'
        )
