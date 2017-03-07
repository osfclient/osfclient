#! /usr/bin/env python3
from osfclient.utils.authentication import AuthClient
from osfclient.client import osf
import argparse

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
    u = oo.get_node('7g6vu')

    print('looking at: {}'.format(u.title))
    
    s = u.get_storage()

    chillun = s.get_children()
    for c in chillun:
        attr = c.raw['attributes']

        name = attr['name']
        size = int(attr['size'])

        print('Downloading {}kb file: {}...'.format(int(size / 1000), name))

        # download the file contents
        response = oo.request_session.get(c.raw['links']['download'])

        with open(name, 'wb') as fp:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                fp.write(response.content)
        print('...done. writing!')


if __name__ == '__main__':
    main()
