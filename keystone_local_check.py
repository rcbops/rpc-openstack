#!/usr/bin/env python
import maas_common
import re
import sys

ENDPOINT = 'http://127.0.0.1:35357/v2.0'


def check(auth_ref):
    keystone = maas_common.get_keystone_client(auth_ref, endpoint=ENDPOINT)

    if keystone is None:
        print 'status err Unable to obtain valid keystone client, ' \
              'cannot proceed'
        sys.exit(1)

    users = keystone.users.list()

    print 'status OK'
    print 'metric keystone_local_status uint32 1'


def main():
    auth_ref = maas_common.get_auth_ref()
    check(auth_ref)

if __name__ == "__main__":
    main()
