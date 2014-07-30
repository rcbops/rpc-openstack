#!/usr/bin/env python

from maas_common import (status_ok, status_err, metric, get_keystone_client,
                         get_auth_ref)
import requests
from requests import exceptions as exc

# NOTE(mancdaz): until https://review.openstack.org/#/c/74602/
# lands, there is no way to pass a custom (local) endpoint to
# cinderclient. Only way to test local is direct http. :sadface:


def check(auth_ref):

    keystone = get_keystone_client(auth_ref)
    tenant_id = keystone.tenant_id
    auth_token = keystone.auth_token
    volume_endpoint = 'http://127.0.0.1:8776/v1/%s' % tenant_id

    s = requests.Session()

    s.headers.update(
        {'Content-type': 'application/json',
         'x-auth-token': auth_token})

    try:
        r = s.get('%s/volumes' % volume_endpoint,
                  verify=False,
                  timeout=10)
    except (exc.ConnectionError,
            exc.HTTPError,
            exc.Timeout) as e:
        status_err(str(e))

    if not r.ok:
        status_err('could not get response from cinder api')

    milliseconds = r.elapsed.total_seconds() * 1000

    status_ok()
    metric('cinder_api_local_status', 'uint32', 1)
    metric('cinder_api_response_time', 'uint32', milliseconds)


def main():
    auth_ref = get_auth_ref()
    check(auth_ref)


if __name__ == "__main__":
    main()
