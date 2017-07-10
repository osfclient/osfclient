"""Utility functions

Helpers and other assorted functions.
"""

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


def makedirs(path, mode=511, exist_ok=False):
    # mode 0777 is 511 in decimal
    if six.PY3:
        return os.makedirs(path, mode, exist_ok)
    else:
        if os.path.exists(path) and exist_ok:
            return None
        else:
            return os.makedirs(path, mode)


def file_empty(fp):
    """Determine if a file is empty or not."""
    # for python 2 we need to use a homemade peek()
    if six.PY2:
        contents = fp.read()
        fp.seek(0)
        return not bool(contents)

    else:
        return not fp.peek()
