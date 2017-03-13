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

    for obj in filetree.get_project_files(args.project):
        output_filename = os.path.join(out_path, obj.path)
        output_dir = os.path.dirname(output_filename)
        os.makedirs(output_dir, exist_ok=True)

        if obj.is_file:
            output_filename = os.path.join(out_path, obj.path)
            
            print('Downloading: {} to {}...'.format(obj.path, out_path))

            # download the file contents
            response = obj.get_download()

            with open(output_filename, 'wb') as fp:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    fp.write(response.content)
        else:
            continue


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
