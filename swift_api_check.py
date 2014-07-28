#!/usr/bin/env python

import sys
from time import time
from swiftclient import client
import maas_common


def check(auth_ref):
    keystone = maas_common.get_keystone_client(auth_ref)
    if keystone is None:
        print 'status err Unable to obtain valid keystone client, ' \
              'cannot proceed'
        sys.exit(1)

    endpoint = keystone.service_catalog.url_for(service_type='object-store',
                                                endpoint_type='publicURL')
    auth_token = keystone.auth_ref['token']['id']

    swift = client.Connection(preauthurl=endpoint, preauthtoken=auth_token)
    start_time = time()
    account, containers = swift.get_account()
    request_time = time() - start_time
    total_objects = sum([c['count'] for c in containers])
    total_bytes = sum([c['bytes'] for c in containers])

    print 'status OK'
    print 'metric swift_response_time double %f' % request_time
    print 'metric swift_containers uint32 %d' % len(containers)
    print 'metric swift_objects uint64 %d' % total_objects
    print 'metric swift_bytes uint64 %d' % total_bytes


def main():
    auth_ref = maas_common.get_auth_ref()
    check(auth_ref)


if __name__ == "__main__":
    main()