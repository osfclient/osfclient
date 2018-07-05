from __future__ import print_function
import sys
import six
import argparse
from textwrap import dedent

from .cli import clone, fetch, list_, remove, upload, init
from . import __version__


def main():
    description = dedent("""
    osf is a command-line program to up and download
    files from osf.io.

    These are common osf commands:

        init      Set up a .osfcli.config file
        clone     Copy all files from all storages of a project
        fetch     Fetch an individual file from a project
        list      List all files from all storages for a project
        upload    Upload a new file to an existing project
        remove    Remove a file from a project's storage

    See 'osf <command> -h' to read about a specific command.
    """)
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-u', '--username', default=None,
                        help=('OSF username. Provide your password via '
                              'OSF_PASSWORD environment variable'))
    parser.add_argument('-p', '--project', default=None,
                        help='OSF project ID')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {}'.format(__version__))
    # dest=command stores the name of the command in a variable, this is
    # used later on to retrieve the correct sub-parser
    subparsers = parser.add_subparsers(dest='command')

    # Clone project
    clone_parser = subparsers.add_parser(
        'clone', description=clone.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    clone_parser.set_defaults(func=clone)
    clone_parser.add_argument('output', help='Write files to this directory',
                              default=None, nargs='?')
    clone_parser.add_argument('-U', '--update',
                               help='Overwrite only if local and remote files differ',
                               action='store_true')

    def _add_subparser(name, description, aliases=[]):
        options = {
            'description': description,
            'formatter_class': argparse.RawDescriptionHelpFormatter,
        }
        if six.PY3:
            options['aliases'] = aliases
        return subparsers.add_parser(name, **options)

    init_parser = _add_subparser('init', init.__doc__)
    init_parser.set_defaults(func=init)

    # Fetch an individual file
    fetch_parser = _add_subparser('fetch', fetch.__doc__)
    fetch_parser.set_defaults(func=fetch)
    fetch_parser.add_argument('-f', '--force',
                              help='Force overwriting of local file',
                              action='store_true')
    fetch_parser.add_argument('-U', '--update',
                               help='Overwrite only if local and remote files differ',
                               action='store_true')
    fetch_parser.add_argument('remote', help='Remote path',
                              default=None)
    fetch_parser.add_argument('local', help='Local path',
                              default=None, nargs='?')

    # List all files in a project
    list_parser = _add_subparser('list', list.__doc__, aliases=['ls'])
    list_parser.set_defaults(func=list_)

    # Upload a single file or a directory tree
    upload_parser = _add_subparser('upload', upload.__doc__)
    upload_parser.set_defaults(func=upload)
    upload_parser.add_argument('-f', '--force',
                               help='Force overwriting of remote file',
                               action='store_true')
    upload_parser.add_argument('-U', '--update',
                               help='Overwrite only if local and remote files differ',
                               action='store_true')
    upload_parser.add_argument('-r', '--recursive',
                               help='Recursively upload entire directories',
                               action='store_true')
    upload_parser.add_argument('source', help='Local file')
    upload_parser.add_argument('destination', help='Remote file path')

    # Remove a single file
    remove_parser = _add_subparser('remove', remove.__doc__, aliases=['rm'])
    remove_parser.set_defaults(func=remove)
    remove_parser.add_argument('target', help='Remote file path')

    # Python2 argparse exits with an error when no command is given
    if six.PY2 and len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()
    if 'func' in args:
        # give functions a chance to influence the exit code
        # this setup is so we can print usage for the sub command
        # even if there was an error further down
        try:
            exit_code = args.func(args)
        except SystemExit as e:
            exit_code = e.code

        if exit_code is not None:
            sub_parser = subparsers.choices[args.command]
            sub_parser.print_usage(file=sys.stderr)
            print('{} {}: error:'.format(parser.prog, args.command),
                  file=sys.stderr, end=' ')
            sys.exit(exit_code)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
