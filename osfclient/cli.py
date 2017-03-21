"""Command line interface to the OSF"""

from .api import OSF


CHUNK_SIZE = int(5e6)


def fetch(args):
    pass


def list_(args):
    username = args.username
    password = None
    if username is not None:
        password = open('pw.txt').read()

    osf = OSF(username=username, password=password)

    project = osf.project(args.project)

    for store in project.storages:
        print(store)
        for file_ in store.files:
            print(file_)
