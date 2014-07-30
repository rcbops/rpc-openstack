#!/usr/bin/env python

from maas_common import (status_ok, status_err, metric, metric_bool,
                         get_auth_ref)
from requests import Session
from requests import exceptions as exc


def check(auth_ref):
    registry_endpoint = 'http://127.0.0.1:9191'
    api_status = 1
    milliseconds = 0
    s = Session()

    s.headers.update(
        {'Content-type': 'application/json',
         'x-auth-token': auth_ref['token']['id']})

    try:
        # /images returns a list of public, non-deleted images
        r = s.get('%s/images' % registry_endpoint, verify=False, timeout=10)
    except (exc.ConnectionError, exc.HTTPError, exc.Timeout):
        api_status = 0
        milliseconds = -1
    except Exception as e:
        status_err(str(e))
    else:
        milliseconds = r.elapsed.total_seconds() * 1000

        if not r.ok:
            api_status = 0

    status_ok()
    metric_bool('glance_registry_local_status', api_status)
    metric('glance_registry_local_response_time', 'int32', milliseconds)


def main():
    auth_ref = get_auth_ref()
    check(auth_ref)


if __name__ == "__main__":
    main()
