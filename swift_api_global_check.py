#!/usr/bin/env python

import sys
from time import time
from swiftclient import client
from maas_common import (status_ok, status_err, metric, get_auth_ref,
                         get_keystone_client)


def check(auth_ref):
    try:
        keystone = get_keystone_client(auth_ref)
        if keystone is None:
            error = 'Unable to obtain valid keystone client, cannot proceed'
            status_err(error)

        endpoint = keystone.service_catalog.url_for(
            service_type='object-store',
            endpoint_type='publicURL')
        auth_token = keystone.auth_ref['token']['id']

        swift = client.Connection(preauthurl=endpoint, preauthtoken=auth_token)
        start_time = time()
        account, containers = swift.get_account()
        request_time = int((time() - start_time) * 1000)
        total_objects = sum([c['count'] for c in containers])
        total_bytes = sum([c['bytes'] for c in containers])
    except Exception as e:
        status_err(str(e))

    status_ok()
    metric('swift_response_time', 'uint32', request_time)
    metric('swift_containers', 'uint32', len(containers))
    metric('swift_objects', 'uint64', total_objects)
    metric('swift_bytes', 'uint64', total_bytes)


def main():
    auth_ref = get_auth_ref()
    check(auth_ref)


if __name__ == "__main__":
    main()
