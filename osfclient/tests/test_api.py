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


def test_address_parameter():
    address = "https://api.test.osf.io/v2"
    assert OSF(address=address).session.base_url == address
    assert OSF(address=address).session.base_url != "https://api.osf.io/v2"


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

@patch.object(OSFSession, 'basic_auth')
@patch('osfclient.models.OSFCore._get')
def test_get_projects(OSFCore_get, session_basic_auth):
    user_me_url = 'https://api.osf.io/v2/users/me/'
    user_nodes_url = "https://api.test.osf.io/v2/users/f3szu/nodes/"

    def test_project(project_list, length):
        def response(url, *args, **kwargs):
            data = {'data': {'relationships': {'nodes': {'links': {'related': {'href': user_nodes_url}}}}}}
            print(url)
            if url == user_me_url:
                return FakeResponse(200, data)
            else:
                return FakeResponse(200, {"data": project_list})

        OSFCore_get.side_effect = response

        osf = OSF()
        osf.login('joe@example.com', 'secret_password')
        projects = osf.projects()

        calls = [call(user_me_url), call(user_nodes_url)]
        OSFCore_get.assert_has_calls(calls)
        assert isinstance(projects, list)
        assert len(projects) == length

        for index, proj in enumerate(projects):
            assert isinstance(proj, Project)
            assert proj.id == project_list[index]["data"]["id"]

    test_project([], 0)
    test_project([project_node], 1)

@patch.object(OSFCore, '_get', return_value=FakeResponse(200, project_node))
def test_get_project(OSFCore_get):
    osf = OSF()
    project = osf.project('f3szh')

    calls = [call('https://api.osf.io/v2/guids/f3szh/'), call('https://api.osf.io/v2/nodes/f3szh/')]
    OSFCore_get.assert_has_calls(calls)
    assert isinstance(project, Project)

@patch.object(OSFCore, '_get', return_value=FakeResponse(200, project_node))
def test_project_metadata(OSFCore_get):
    osf = OSF()
    project = osf.project('f3szh')

    md = project.metadata()
    data = project_node["data"]["attributes"]

    assert data["title"] == md["title"]
    assert data["date_created"] == md["date_created"]
    assert data["date_modified"] == md["date_modified"]
    assert data["description"] == md["description"]
    assert data["category"] == md["category"]
    assert data["tags"] == md["tags"]
    assert data["public"] == md["public"]


@patch.object(OSFCore, '_get', return_value=FakeResponse(200, project_node))
def test_project_metadata_only_mutable(OSFCore_get):
    osf = OSF()
    project = osf.project('f3szh')

    md = project.metadata(only_mutable=True)
    data = project_node["data"]["attributes"]

    assert data["title"] == md["title"]
    assert data["description"] == md["description"]
    assert data["category"] == md["category"]
    assert data["tags"] == md["tags"]
    assert data["public"] == md["public"]

    with pytest.raises(KeyError):
        md["date_created"]
        md["date_modified"]


@patch.object(OSFCore, '_get', return_value=FakeResponse(200, registration_node))
def test_get_registration(OSFCore_get):
    osf = OSF()
    project = osf.project('f3szh')

    calls = [call('https://api.osf.io/v2/guids/f3szh/'), call('https://api.osf.io/v2/registrations/f3szh/')]
    OSFCore_get.assert_has_calls(calls)
    assert isinstance(project, Project)


@patch.object(OSFCore, '_get', return_value=FakeResponse(200, fake_node))
def test_get_fake(OSFCore_get):
    osf = OSF()
    with pytest.raises(OSFException) as exc:
        osf.project('f3szh')

    assert exc.value.args[0] == 'f3szh is unrecognized type fakes. Clone supports projects and registrations'
    OSFCore_get.assert_called_once_with(
        'https://api.osf.io/v2/guids/f3szh/'
        )


@patch.object(OSFCore, '_get', return_value=FakeResponse(404, project_node))
def test_failed_get_project(OSFCore_get):
    osf = OSF()
    with pytest.raises(RuntimeError):
        osf.project('f3szh')

    OSFCore_get.assert_called_once_with(
        'https://api.osf.io/v2/guids/f3szh/'
        )
