import sys
import argparse

from .cli import fetch, list_, upload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', default=None,
                        help=('OSF username. Provide password via '
                              'OSF_PASSWORD environment variable.'))
    subparsers = parser.add_subparsers()

    # Fetch files
    fetch_parser = subparsers.add_parser('fetch',
                                         description=('Fetch all files from all'
                                                      ' storages for project.')
                                         )
    fetch_parser.set_defaults(func=fetch)
    fetch_parser.add_argument('project', help='OSF project ID')
    fetch_parser.add_argument('output', help='Write files to this directory',
                              default=None, nargs='?')

    # List files
    list_parser = subparsers.add_parser('list', aliases=['ls'],
                                        description=('List all files from all'
                                                     ' storages for project.')
                                        )
    list_parser.set_defaults(func=list_)
    list_parser.add_argument('project', help='OSF project ID')

    # Upload a file
    upload_parser = subparsers.add_parser('upload',
                                          description=('Upload a new file to'
                                                       ' an existing project.')
                                          )
    upload_parser.set_defaults(func=upload)
    upload_parser.add_argument('project', help='OSF project ID')
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
