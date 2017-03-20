from osfclient.api import OSFSession


def test_basic_auth():
    session = OSFSession()
    session.basic_auth('joe@example.com', 'secret_password')
    assert session.auth == ('joe@example.com', 'secret_password')
    assert 'Authorization' not in session.headers


def test_basic_build_url():
    session = OSFSession()
    url = session.build_url("some", "path")
    assert url.startswith(session.base_url)
    assert url.endswith("/some/path/")
