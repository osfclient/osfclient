#! /usr/bin/env python3
from osfclient.utils.authentication import AuthClient
from osfclient.client import osf
from osfclient import filetree
import argparse
import os

CHUNK_SIZE=int(5e6)
do_login = False


def main():
    p = argparse.ArgumentParser()
    p.add_argument('project_id', help="OSF project ID, e.g. 7g7vu")
    args = p.parse_args()
    auth_client = AuthClient()

    # see osfsync/gui/qt/login.py for OTP info
    if do_login:
        username='ctbrown@ucdavis.edu'
        password=open('pw.txt').read()
        _ = auth_client.login(username=username, password=password,
                              otp=None)

    oo = osf.OSFClient()

    for obj in filetree.get_project_files(args.project_id):
        if obj.is_file:
            size = obj.size
            path = obj.path

            print('Downloading {}kb file: {}...'.format(int(size / 1000),
                                                        path))

            # download the file contents
            response = obj.get_download()

            with open(path, 'wb') as fp:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    fp.write(response.content)
            print('...done. writing!')
        else:
            path = obj.path
            try:
                os.mkdir(path)
            except FileExistsError:
                continue


if __name__ == '__main__':
    main()
