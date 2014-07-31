#!/usr/bin/env python

from requests import Session
from requests import exceptions as exc
from maas_common import (get_auth_ref, get_keystone_client, metric_bool,
                         metric, status_ok, status_err)


def check_heat(tenant, token):
    s = Session()
    s.headers.update(
        {'Content-type': 'application/json',
         'x-auth-token': token})

    api_is_up = True
    try:
        r = s.get('http://127.0.0.1:8004/v1/{0}/build_info'.format(tenant),
                  verify=False, timeout=10)
    except (exc.ConnectionError, exc.HTTPError, exc.Timeout):
        api_is_up = False
        milliseconds = -1
    except Exception as e:
        status_err(str(e))
    else:
        milliseconds = r.elapsed.total_seconds() * 1000.0
        api_is_up = r.ok

    status_ok()
    metric_bool('heat_api_local_status', api_is_up)
    metric('heat_local_response_time', 'int32', milliseconds)


def main():
    keystone = get_keystone_client(get_auth_ref())
    tenant = keystone.tenant_id
    token = keystone.auth_ref['token']['id']

    check_heat(tenant, token)

if __name__ == "__main__":
    main()
