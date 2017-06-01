import sys
import argparse
from textwrap import dedent

from .cli import clone, fetch, list_, remove, upload


def main():
    description = dedent("""
    osf is a command-line program to up and download
    files from osf.io.

    These are common osf commands:

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
                              'OSF_PASSWORD environment variable.'))
    parser.add_argument('-p', '--project', default=None, help='OSF project ID')
    # dest=command stores the name of the command in a variable, this is
    # used later on to retrieve the correct sub-parser
    subparsers = parser.add_subparsers(dest='command')

    # Clone project
    clone_parser = subparsers.add_parser(
        'clone', description=clone.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    clone_parser.set_defaults(func=clone)
    clone_parser.add_argument('project', help='OSF project ID')
    clone_parser.add_argument('output', help='Write files to this directory',
                              default=None, nargs='?')

    # Fetch an individual file
    fetch_parser = subparsers.add_parser(
        'fetch', description=fetch.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
        )
    fetch_parser.set_defaults(func=fetch)
    fetch_parser.add_argument('-f', help='Force overwriting of local file',
                              action='store_true')
    fetch_parser.add_argument('remote', help='Remote path',
                              default=None)
    fetch_parser.add_argument('local', help='Local path',
                              default=None, nargs='?')

    # List all files in a project
    list_parser = subparsers.add_parser(
        'list', aliases=['ls'], description=list_.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
        )
    list_parser.set_defaults(func=list_)

    # Upload a single file
    upload_parser = subparsers.add_parser(
        'upload', description=upload.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
        )
    upload_parser.set_defaults(func=upload)
    upload_parser.add_argument('source', help='Local file')
    upload_parser.add_argument('destination', help='Remote file path')

    # Remove a single file
    remove_parser = subparsers.add_parser(
        'remove', aliases=['rm'], description=remove.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
        )
    remove_parser.set_defaults(func=remove)
    remove_parser.add_argument('target', help='Remote file path')

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
