import argparse

from .cli import fetch, list_


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

    args = parser.parse_args()
    if 'func' in args:
        args.func(args)


if __name__ == "__main__":
    main()
