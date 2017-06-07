from mock import call, patch

from osfclient.utils import norm_remote_path
from osfclient.utils import makedirs
from osfclient.utils import split_storage


def test_default_storage():
    store, path = split_storage('foo/bar/baz')
    assert store == 'osfstorage'
    assert path == 'foo/bar/baz'

    store, path = split_storage('/foo/bar/baz')
    assert store == 'osfstorage'
    assert path == 'foo/bar/baz'


def test_split_storage():
    store, path = split_storage('osfstorage/foo/bar/baz')
    assert store == 'osfstorage'
    assert path == 'foo/bar/baz'

    store, path = split_storage('github/foo/bar/baz')
    assert store == 'github'
    assert path == 'foo/bar/baz'

    store, path = split_storage('/github/foo/bar/baz')
    assert store == 'github'
    assert path == 'foo/bar/baz'


def test_norm_remote_path():
    path = 'foo/bar/baz.txt'

    new_path = norm_remote_path(path)
    assert new_path == path

    new_path = norm_remote_path('/' + path)
    assert new_path == path


@patch('osfclient.utils.os.path')
@patch('osfclient.utils.os.makedirs')
def test_makedirs_py2(mock_makedirs, mock_path):
    # pretend to be in python 2 land
    # path already exists, expect to call makedirs and that will raise
    mock_path.exists.return_value = True
    with patch('osfclient.utils.six.PY3', False):
        makedirs('/this/path/exists')

    expected = [call('/this/path/exists', 511)]
    assert expected == mock_makedirs.mock_calls


@patch('osfclient.utils.os.path')
@patch('osfclient.utils.os.makedirs')
def test_makedirs_exist_ok_py2(mock_makedirs, mock_path):
    # pretend to be in python 2 land
    # path already exists, expect NOT to call makedirs as we set exist_ok
    mock_path.exists.return_value = True
    with patch('osfclient.utils.six.PY3', False):
        makedirs('/this/path/exists', exist_ok=True)

    assert not mock_makedirs.called


@patch('osfclient.utils.os.path')
@patch('osfclient.utils.os.makedirs')
def test_makedirs_doesnt_exist_py2(mock_makedirs, mock_path):
    # pretend to be in python 2 land
    mock_path.exists.return_value = False
    with patch('osfclient.utils.six.PY3', False):
        makedirs('/this/path/doesnt/exists')

    expected = [call('/this/path/doesnt/exists', 511)]
    assert expected == mock_makedirs.mock_calls


@patch('osfclient.utils.os.makedirs')
def test_makedirs_py3(mock_makedirs):
    # just check stuff get's forwarded
    with patch('osfclient.utils.six.PY3', True):
        makedirs('/this/path/exists', exist_ok=True)

    expected = [call('/this/path/exists', 511, True)]
    assert expected == mock_makedirs.mock_calls
