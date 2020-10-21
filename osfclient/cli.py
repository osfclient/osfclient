"""Command line interface to the OSF

These functions implement the functionality of the command-line interface.
"""
from __future__ import print_function

from functools import wraps
import getpass
import os
import sys

from six.moves import configparser
from six.moves import input

from tqdm import tqdm

from .api import OSF
from .exceptions import UnauthorizedException
from .utils import norm_remote_path, split_storage, makedirs, checksum


def config_from_file():
    if os.path.exists(".osfcli.config"):
        config_ = configparser.ConfigParser()
        config_.read(".osfcli.config")

        # for python2 compatibility
        config = dict(config_.items('osf'))

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

    token = os.getenv("OSF_TOKEN")
    if token is not None:
        config['token'] = token

    return config


def _get_username(args, config):
    if args.username is None:
        username = config.get('username')
    else:
        username = args.username
    return username


def _setup_osf(args):
    # Command line options have precedence over environment variables,
    # which have precedence over the config file.
    config = config_from_env(config_from_file())

    username = _get_username(args, config)

    project = config.get('project')
    if args.project is None:
        args.project = project
    # still None? We are in trouble
    if args.project is None:
        sys.exit('You have to specify a project ID via the command line,'
                 ' configuration file or environment variable.')

    token = config.get('token', None)

    password = None
    if username is not None and token is None:
        password = os.getenv("OSF_PASSWORD")

        # Prompt user when password is not set
        if password is None:
            password = getpass.getpass('Please input your password: ')

    return OSF(username=username, password=password, token=token)


def might_need_auth(f):
    """Decorate a CLI function that might require authentication.

    Catches any UnauthorizedException raised, prints a helpful message and
    then exits.
    """
    @wraps(f)
    def wrapper(cli_args):
        try:
            return_value = f(cli_args)
        except UnauthorizedException as e:
            config = config_from_env(config_from_file())
            username = _get_username(cli_args, config)

            if username is None:
                sys.exit("Please set a username (run `osf -h` for details).")
            else:
                sys.exit("You are not authorized to access this project.")

        return return_value

    return wrapper


def init(args):
    """Initialize or edit an existing .osfcli.config file."""
    # reading existing config file, convert to configparser object
    config = config_from_file()
    config_ = configparser.ConfigParser()
    config_.add_section('osf')
    if 'username' not in config.keys():
        config_.set('osf', 'username', '')
    else:
        config_.set('osf', 'username', config['username'])
    if 'project' not in config.keys():
        config_.set('osf', 'project', '')
    else:
        config_.set('osf', 'project', config['project'])

    # now we can start asking for new values
    print('Provide a username for the config file [current username: {}]:'.format(
          config_.get('osf', 'username')))
    username = input()
    if username:
        config_.set('osf', 'username', username)

    print('Provide a project for the config file [current project: {}]:'.format(
          config_.get('osf', 'project')))
    project = input()
    if project:
        config_.set('osf', 'project', project)

    cfgfile = open(".osfcli.config", "w")
    config_.write(cfgfile)
    cfgfile.close()


@might_need_auth
def clone(args):
    """Copy all files from all storages of a project.

    The output directory defaults to the current directory.

    If the project is private you need to specify a username.

    If args.update is True, overwrite any existing local files only if local and
    remote files differ.
    """
    osf = _setup_osf(args)
    project = osf.project(args.project)
    output_dir = args.project
    if args.output is not None:
        output_dir = args.output

    with tqdm(unit='files') as pbar:
        for store in project.storages:
            prefix = os.path.join(output_dir, store.name)

            for file_ in store.files:
                path = file_.path
                if path.startswith('/'):
                    path = path[1:]

                path = os.path.join(prefix, path)
                if os.path.exists(path) and args.update:
                    if checksum(path) == file_.hashes.get('md5'):
                        continue
                directory, _ = os.path.split(path)
                makedirs(directory, exist_ok=True)

                with open(path, "wb") as f:
                    file_.write_to(f)

                pbar.update()


@might_need_auth
def fetch(args):
    """Fetch an individual file from a project.

    The first part of the remote path is interpreted as the name of the
    storage provider. If there is no match the default (osfstorage) is
    used.

    The local path defaults to the name of the remote file.

    If the project is private you need to specify a username.

    If args.force is True, write local file even if that file already exists.
    If args.force is False but args.update is True, overwrite an existing local
    file only if local and remote files differ.
    """
    storage, remote_path = split_storage(args.remote)

    local_path = args.local
    if local_path is None:
        _, local_path = os.path.split(remote_path)

    local_path_exists = os.path.exists(local_path)
    if local_path_exists and not args.force and not args.update:
        sys.exit("Local file %s already exists, not overwriting." % local_path)

    directory, _ = os.path.split(local_path)
    if directory:
        makedirs(directory, exist_ok=True)

    osf = _setup_osf(args)
    project = osf.project(args.project)

    store = project.storage(storage)
    for file_ in store.files:
        if norm_remote_path(file_.path) == remote_path:
            if local_path_exists and not args.force and args.update:
                if file_.hashes.get('md5') == checksum(local_path):
                    print("Local file %s already matches remote." % local_path)
                    break
            with open(local_path, 'wb') as fp:
                file_.write_to(fp)

            # only fetching one file so we are done
            break


@might_need_auth
def list_(args):
    """List all files from all storages for project.

    If the project is private you need to specify a username.
    """
    osf = _setup_osf(args)

    project = osf.project(args.project)

    for store in project.storages:
        prefix = store.name
        for file_ in store.files:
            path = file_.path
            if path.startswith('/'):
                path = path[1:]

            print(os.path.join(prefix, path))


@might_need_auth
def upload(args):
    """Upload a new file to an existing project.

    The first part of the remote path is interpreted as the name of the
    storage provider. If there is no match the default (osfstorage) is
    used.

    If the project is private you need to specify a username.

    To upload a whole directory (and all its sub-directories) use the `-r`
    command-line option. If your source directory name ends in a / then
    files will be created directly in the remote directory. If it does not
    end in a slash an extra sub-directory with the name of the local directory
    will be created.

    To place contents of local directory `foo` in remote directory `bar/foo`:
    $ osf upload -r foo bar
    To place contents of local directory `foo` in remote directory `bar`:
    $ osf upload -r foo/ bar
    """
    osf = _setup_osf(args)
    if osf.username is None or osf.password is None:
        sys.exit('To upload a file you need to provide a username and'
                 ' password.')

    project = osf.project(args.project)
    storage, remote_path = split_storage(args.destination)

    store = project.storage(storage)
    if args.recursive:
        if not os.path.isdir(args.source):
            raise RuntimeError("Expected source ({}) to be a directory when "
                               "using recursive mode.".format(args.source))

        # local name of the directory that is being uploaded
        _, dir_name = os.path.split(args.source)

        for root, _, files in os.walk(args.source):
            subdir_path = os.path.relpath(root, args.source)
            for fname in files:
                local_path = os.path.join(root, fname)
                with open(local_path, 'rb') as fp:
                    # build the remote path + fname
                    name = os.path.join(remote_path, dir_name, subdir_path,
                                        fname)
                    store.create_file(name, fp, force=args.force,
                                      update=args.update)

    else:
        with open(args.source, 'rb') as fp:
            store.create_file(remote_path, fp, force=args.force,
                              update=args.update)


@might_need_auth
def remove(args):
    """Remove a file from the project's storage.

    The first part of the remote path is interpreted as the name of the
    storage provider. If there is no match the default (osfstorage) is
    used.
    """
    osf = _setup_osf(args)
    if osf.username is None or osf.password is None:
        sys.exit('To remove a file you need to provide a username and'
                 ' password.')

    project = osf.project(args.project)

    storage, remote_path = split_storage(args.target)

    store = project.storage(storage)
    for f in store.files:
        if norm_remote_path(f.path) == remote_path:
            f.remove()
