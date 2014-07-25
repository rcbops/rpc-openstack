#!/usr/bin/env python

import maas_common
import sys

IMAGE_ENDPOINT = 'http://127.0.0.1:9292'


def check(token):
    glance = maas_common.get_glance_client(token, IMAGE_ENDPOINT)
    if glance is None:
        print 'status err Unable to obtain valid glance client, ' \
              'cannot proceed'
        sys.exit(1)

    print 'status OK'
    print 'metric glance_api_local_status uint32 1'


def main():
    auth_ref = maas_common.get_auth_ref()
    token = auth_ref['token']['id']
    check(token)


if __name__ == "__main__":
    main()
