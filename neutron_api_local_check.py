#!/usr/bin/env python

import maas_common
import sys

NETWORK_ENDPOINT = 'http://127.0.0.1:9696'


def check(token):

    neutron = maas_common.get_neutron_client(token, NETWORK_ENDPOINT)

    if neutron is None:
        print 'status err Unable to obtain valid neutron client, ' \
              'cannot proceed'
        sys.exit(1)

    print 'status OK'
    print 'metric neutron_api_local_status uint32 1'


def main():
    auth_ref = maas_common.get_auth_ref()
    token = auth_ref['token']['id']
    check(token)


if __name__ == "__main__":
    main()
