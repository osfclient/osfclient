import sys
import argparse

from .cli import clone, fetch, list_, upload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', default=None,
                        help=('OSF username. Provide password via '
                              'OSF_PASSWORD environment variable.'))
    parser.add_argument('-p', '--project', default=None, help='OSF project.')
    subparsers = parser.add_subparsers()

    # Clone project
    clone_parser = subparsers.add_parser('clone',
                                         description=('Copy all files from all'
                                                      ' storages for project.')
                                         )
    clone_parser.set_defaults(func=clone)
    clone_parser.add_argument('project', help='OSF project ID')
    clone_parser.add_argument('output', help='Write files to this directory',
                              default=None, nargs='?')

    # Fetch an individual file
    fetch_parser = subparsers.add_parser('fetch',
                                         description=('Fetch an individual'
                                                      ' file from a project.')
                                         )
    fetch_parser.set_defaults(func=fetch)
    fetch_parser.add_argument('-f', help='Force overwriting of local file',
                              action='store_true')
    fetch_parser.add_argument('remote', help='Remote path',
                              default=None)
    fetch_parser.add_argument('local', help='Local path',
                              default=None, nargs='?')

    # List all files in a project
    list_parser = subparsers.add_parser('list', aliases=['ls'],
                                        description=('List all files from all'
                                                     ' storages for project.')
                                        )
    list_parser.set_defaults(func=list_)

    # Upload a single file
    upload_parser = subparsers.add_parser('upload',
                                          description=('Upload a new file to'
                                                       ' an existing project.')
                                          )
    upload_parser.set_defaults(func=upload)
    upload_parser.add_argument('source', help='Local file')
    upload_parser.add_argument('destination', help='Remote file path')

    args = parser.parse_args()
    if 'func' in args:
        # give functions a chance to influence the exit code
        exit_code = args.func(args)
        if exit_code is not None:
            sys.exit(exit_code)


if __name__ == "__main__":
    main()
