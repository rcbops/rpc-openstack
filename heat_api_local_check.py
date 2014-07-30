#!/usr/bin/env python

from requests import Session
from requests import exceptions as exc
from maas_common import (get_auth_ref, get_keystone_client,
                         metric, status_ok, status_err)


def check_heat(tenant, token):
    s = Session()
    s.headers.update(
        {'Content-type': 'application/json',
         'x-auth-token': token})

    api_status = 1
    try:
        r = s.get('http://127.0.0.1:8004/v1/{0}/build_info'.format(tenant), verify=False, timeout=10)
    except (exc.ConnectionError, exc.HTTPError, exc.Timeout):
        api_status = 0
        milliseconds = -1
    except Exception as e:
        status_err(str(e))
    else:
        milliseconds = r.elapsed.total_seconds() * 1000.0
        if not r.ok:
            api_status = 0

    status_ok()
    metric('heat_api_local_status', 'uint32', api_status)
    metric('heat_local_response_time', 'int32', milliseconds)


def main():
    keystone = get_keystone_client(get_auth_ref())
    tenant = keystone.tenant_id
    token = keystone.auth_ref['token']['id']

    check_heat(tenant, token)

if __name__ == "__main__":
    main()
