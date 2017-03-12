"""Open Science Framework client"""

import os

from osfclient.utils.authentication import AuthClient
from osfclient.client import osf
from osfclient import filetree

CHUNK_SIZE = int(5e6)


def fetch(args):
    out_path = os.path.realpath(args.output)

    auth_client = AuthClient()
    username = args.username
    if username:
        password = open('pw.txt').read()

        # this sets a global/singleton object => OSFClient.
        auth_client.login(username=username, password=password, otp=None)

    # see auth_client, above, for authentication foo.
    oo = osf.OSFClient()
    project = oo.get_node(args.project)

    print('looking at: {}'.format(project.title))

    storages = osf.NodeStorage.load(oo.request_session, args.project)

    for storage in storages:
        os.makedirs(os.path.join(out_path, storage.name), exist_ok=True)
        for c in storage.get_children():
            attr = c.raw['attributes']

            name = attr['name']

            output_filename = os.path.join(out_path, storage.name, name)

            print('Downloading: {} to {}...'.format(name, output_filename))

            # download the file contents
            response = oo.request_session.get(c.raw['links']['download'])

            with open(output_filename, 'wb') as fp:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    fp.write(response.content)


def list_(args):
    auth_client = AuthClient()
    username = args.username
    if username:
        password = open('pw.txt').read()

        # this sets a global/singleton object => OSFClient.
        auth_client.login(username=username, password=password, otp=None)

    # see auth_client, above, for authentication foo.

    filenames = []
    for obj in filetree.get_project_files(args.project):
        filenames.append(obj.path)

    print("\n".join(filenames))
