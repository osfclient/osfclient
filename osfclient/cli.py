"""Command line interface to the OSF"""

import os
import configparser
import sys

from .api import OSF
from .utils import norm_remote_path, split_storage


def config_from_file():
    if os.path.exists(".osfcli.config"):
        config_ = configparser.ConfigParser()
        config_.read(".osfcli.config")

        config = config_['osf']

    else:
        config = {}

    return config


def config_from_env(config):
    username = os.getenv("OSF_USERNAME")
    if username is not None:
        config['username'] = username

    project = os.getenv("OSF_PROJECT")
    if project is not None:
        config['project'] = project

    return config


def _setup_osf(args):
    # Command line options have precedence over environment variables,
    # which have precedence over the config file.
    config = config_from_env(config_from_file())

    if args.username is None:
        username = config.get('username')
    else:
        username = args.username

    project = config.get('project')
    if args.project is None:
        args.project = project
    # still None? We are in trouble
    if args.project is None:
        print('You have to specify a project ID via the command line,'
              ' configuration file or environment variable.')
        sys.exit(1)

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
