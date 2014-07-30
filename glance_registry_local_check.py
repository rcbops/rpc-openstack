#!/usr/bin/env python

from maas_common import (status_ok, status_err, metric, get_keystone_client,
                         get_auth_ref)
from requests import Session
from requests import exceptions as exc


def check(auth_ref):
    keystone = get_keystone_client(auth_ref)
    tenant_id = keystone.tenant_id
    auth_token = keystone.auth_token
    registry_endpoint = 'http://127.0.0.1:9191'

    s = Session()

    s.headers.update(
        {'Content-type': 'application/json',
         'x-auth-token': auth_token})

    try:
        # /images returns a list of public, non-deleted images
        r = s.get('%s/images' % registry_endpoint, verify=False, timeout=10)
    except (exc.ConnectionError,
            exc.HTTPError,
            exc.Timeout) as e:
        status_err(str(e))

    if not r.ok:
        status_err('could not get a 200 response from glance-registry')

    milliseconds = r.elapsed.total_seconds() * 1000

    status_ok()
    metric('glance_registry_local_status', 'uint32', 1)
    metric('glance_registry_local_response_time', 'uint32', milliseconds)


def main():
    auth_ref = get_auth_ref()
    check(auth_ref)


if __name__ == "__main__":
    main()
