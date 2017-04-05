from osfclient.utils import norm_remote_path
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
