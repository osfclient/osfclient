"""Open Science Framework client"""

import os

from osfclient.utils.authentication import AuthClient
from osfclient.client import osf

CHUNK_SIZE = int(5e6)


def fetch(args):
    auth_client = AuthClient()
    username = 'betatim@gmail.com'
    password = open('pw.txt').read()

    out_path = os.path.realpath(args.output)

    auth_client.login(username=username, password=password, otp=None)

    oo = osf.OSFClient()
    project = oo.get_node(args.project)

    print('looking at: {}'.format(project.title))

    storages = osf.NodeStorage.load(oo.request_session, args.project)

    for storage in storages:
        os.makedirs(os.path.join(out_path, storage.name), exist_ok=True)
        for c in storage.get_children():
            attr = c.raw['attributes']

            name = attr['name']

            print('Downloading: {}...'.format(name))

            # download the file contents
            response = oo.request_session.get(c.raw['links']['download'])

            with open(os.path.join(out_path, storage.name, name), 'wb') as fp:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    fp.write(response.content)


def list_(args):
    print('listing', args)
