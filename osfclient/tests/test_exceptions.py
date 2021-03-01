import pytest

import osfclient.exceptions as exc


def test_400():
    with pytest.raises(exc.BadRequest) as e:
        exc.raise_unexp_status(400, msg="Test.")
    assert str(e.value) == 'Test.The request was unacceptable, often due' \
                           ' to a missing required parameter or malformed data.'

    with pytest.raises(exc.BadRequest) as e:
        exc.raise_unexp_status(400, expected_code=1)
    assert str(e.value) == 'Response has status code 400 not 1.The request' \
                           ' was unacceptable, often due to a missing' \
                           ' required parameter or malformed data.'


def test_401():
    with pytest.raises(exc.UnauthorizedException) as e:
        exc.raise_unexp_status(401, msg="Test.")
    assert str(e.value) == 'Test.The request requires user authentication, which was not provided.'

    with pytest.raises(exc.UnauthorizedException) as e:
        exc.raise_unexp_status(401, expected_code=1)
    assert str(e.value) == 'Response has status code 401 not 1.The request ' \
                           'requires user authentication, which was not provided.'


def test_404():
    with pytest.raises(exc.NotFound) as e:
        exc.raise_unexp_status(404, msg="Test.")
    assert str(e.value) == 'Test.The requested resource does not exist.'

    with pytest.raises(exc.NotFound) as e:
        exc.raise_unexp_status(404, expected_code=1)
    assert str(e.value) == 'Response has status code 404 not 1.The' \
                           ' requested resource does not exist.'


def test_410():
    with pytest.raises(exc.Gone) as e:
        exc.raise_unexp_status(410, msg="Test.")
    assert str(e.value) == 'Test.The requested resource is no longer' \
                           ' available, most likely because it was deleted.'

    with pytest.raises(exc.Gone) as e:
        exc.raise_unexp_status(410, expected_code=1)
    assert str(e.value) == 'Response has status code 410 not 1.The requested' \
                           ' resource is no longer available, most likely because it was deleted.'


def test_429():
    with pytest.raises(exc.ToManyRequests) as e:
        exc.raise_unexp_status(429, msg="Test.")
    assert str(e.value) == 'Test.Too many requests have been sent. See' \
                    ' https://help.osf.io/hc/en-us/articles/360054528874-OSF-Storage-Caps' \
                    ' for details.'

    with pytest.raises(exc.ToManyRequests) as e:
        exc.raise_unexp_status(429, expected_code=1)
    assert str(e.value) == 'Response has status code 429 not 1.Too many requests have been sent. See' \
                           ' https://help.osf.io/hc/en-us/articles/360054528874-OSF-Storage-Caps' \
                           ' for details.'


def test_5xx():
    with pytest.raises(exc.ServerError) as e:
        exc.raise_unexp_status(500, msg="Test.")
    assert str(e.value) == 'Test.The API server encountered an unexpected error.'

    with pytest.raises(exc.ServerError) as e:
        exc.raise_unexp_status(503, expected_code=1)
    assert str(e.value) == 'Response has status code 503 not 1.The API server encountered an unexpected error.'


def test_other_code():
    with pytest.raises(exc.OSFException) as e:
        exc.raise_unexp_status(300, msg='Test.')
    assert str(e.value) == 'Test.'

    with pytest.raises(exc.OSFException) as e:
        exc.raise_unexp_status(303)
    assert str(e.value) == 'Response has status code 303 not 200.'

    with pytest.raises(exc.OSFException) as e:
        exc.raise_unexp_status(303, expected_code=204)
    assert str(e.value) == 'Response has status code 303 not 204.'
