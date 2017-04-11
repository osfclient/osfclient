"""Command line interface to the OSF"""

import os

from .api import OSF
from .utils import norm_remote_path, split_storage


def _setup_osf(args):
    # command line argument overrides environment variable
    username = os.getenv("OSF_USERNAME")
    if args.username is not None:
        username = args.username

    password = None
    if username is not None:
        password = os.getenv("OSF_PASSWORD")

    return OSF(username=username, password=password)


def clone(args):
    osf = _setup_osf(args)
    project = osf.project(args.project)
    output_dir = args.project
    if args.output is not None:
        output_dir = args.output

    for store in project.storages:
        prefix = os.path.join(output_dir, store.name)

        for file_ in store.files:
            path = file_.path
            if path.startswith('/'):
                path = path[1:]

            path = os.path.join(prefix, path)
            directory, _ = os.path.split(path)
            os.makedirs(directory, exist_ok=True)

            with open(path, "wb") as f:
                file_.write_to(f)


def fetch(args):
    storage, remote_path = split_storage(args.remote)

    local_path = args.local
    if local_path is None:
        _, local_path = os.path.split(remote_path)

    if os.path.exists(local_path):
        print("Local file %s already exists, not "
              "overwriting." % local_path)
        return 1

    directory, _ = os.path.split(local_path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    osf = _setup_osf(args)
    project = osf.project(args.project)

    store = project.storage(storage)
    for file_ in store.files:
        if norm_remote_path(file_.path) == remote_path:
            with open(local_path, 'wb') as fp:
                file_.write_to(fp)


def list_(args):
    osf = _setup_osf(args)

    project = osf.project(args.project)

    for store in project.storages:
        prefix = store.name
        for file_ in store.files:
            path = file_.path
            if path.startswith('/'):
                path = path[1:]

            print(os.path.join(prefix, path))


def upload(args):
    if args.username is None:
        print('To upload a file you need to provider a username and password.')
        return 1

    osf = _setup_osf(args)

    project = osf.project(args.project)

    storage, remote_path = split_storage(args.destination)

    store = project.storage(storage)
    with open(args.source, 'rb') as fp:
        store.create_file(remote_path, fp)
