#!/usr/bin/env python

from maas_common import (status_ok, status_err, metric, metric_bool,
                         get_keystone_client, get_auth_ref)
from requests import Session
from requests import exceptions as exc


def check(auth_ref):
    # We call get_keystone_client here as there is some logic within to get a
    # new token if previous one is bad.
    keystone = get_keystone_client(auth_ref)
    auth_token = keystone.auth_token
    api_endpoint = 'http://127.0.0.1:9292/v2'

    s = Session()

    s.headers.update(
        {'Content-type': 'application/json',
         'x-auth-token': auth_token})

    try:
        # Hit something that isn't querying the glance-registry, since we
        # query glance-registry in separate checks
        r = s.get('%s/schemas/image' % api_endpoint, verify=False,
                  timeout=10)
    except (exc.ConnectionError, exc.HTTPError, exc.Timeout):
        status_ok()
        metric_bool('glance_api_local_status', False)
    except Exception as e:
        status_err(str(e))
    else:
        milliseconds = r.elapsed.total_seconds() * 1000
        status_ok()
        metric_bool('glance_api_local_status', True)
        metric('glance_api_local_response_time', 'uint32', milliseconds, 'ms')


def main():
    auth_ref = get_auth_ref()
    check(auth_ref)


if __name__ == "__main__":
    main()
