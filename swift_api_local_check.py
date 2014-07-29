#!/usr/bin/env python

import sys
from swiftclient import client
from maas_common import (status_ok, status_err, metric, get_auth_ref,
                         get_keystone_client)


def check(auth_ref):
    try:
        keystone = get_keystone_client(auth_ref)
        if keystone is None:
            status_err('Unable to obtain valid keystone client, cannot proceed')

        endpoint = keystone.service_catalog.url_for(service_type='object-store',
                                                endpoint_type='publicURL')
        auth_token = keystone.auth_ref['token']['id']

        swift = client.Connection(preauthurl=endpoint, preauthtoken=auth_token)
        if swift is None:
            status_err('Unable to obtain valid swift client, cannot proceed')
    except Exception as e:
        status_err(str(e))

    status_ok()
    metric('swift_api_local_status', 'uint32', 1)


def main():
    auth_ref = get_auth_ref()
    check(auth_ref)


if __name__ == "__main__":
    main()
