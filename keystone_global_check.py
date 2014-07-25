#!/usr/bin/env python

import maas_common
import sys


def check(auth_ref):
    keystone = maas_common.get_keystone_client(auth_ref)

    if keystone is None:
        print 'status err Unable to obtain valid keystone client, ' \
              'cannot proceed'
        sys.exit(1)

    users = keystone.users.list()
    enabled = [u for u in users if u.enabled is True]

    print 'status OK'
    print 'metric keystone_users uint32 %d' % len(enabled)


def main():
    auth_ref = maas_common.get_auth_ref()
    check(auth_ref)

if __name__ == "__main__":
    main()
