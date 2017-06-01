import os
import six

KNOWN_PROVIDERS = ['osfstorage', 'github']


def norm_remote_path(path):
    """Normalize `path`.

    All remote paths are absolute.
    """
    path = os.path.normpath(path)
    if path.startswith('/'):
        return path[1:]
    else:
        return path


def split_storage(path, default='osfstorage'):
    """Extract storage name from file path.

    If a path begins with a known storage provider the name is removed
    from the path. Otherwise the `default` storage provider is returned
    and the path is not modified.
    """
    path = norm_remote_path(path)

    for provider in KNOWN_PROVIDERS:
        if path.startswith(provider + '/'):
            if six.PY3:
                return path.split('/', maxsplit=1)
            else:
                return path.split('/', 1)

    return (default, path)
