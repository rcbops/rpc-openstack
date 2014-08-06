#!/usr/bin/env python

import argparse
import requests
from ipaddr import IPv4Address
from maas_common import (status_ok, status_err, metric, get_keystone_client,
                         get_auth_ref)
from requests import exceptions as exc

# NOTE(mancdaz): until https://review.openstack.org/#/c/111051/
# lands, there is no way to pass a custom (local) endpoint to
# cinderclient. Only way to test local is direct http. :sadface:


def check(auth_ref, args):

    keystone = get_keystone_client(auth_ref)
    auth_token = keystone.auth_token
    VOLUME_ENDPOINT = 'http://{ip}:8776/v1/{tenant}' \
                      .format(ip=args.ip, tenant=keystone.tenant_id)

    s = requests.Session()

    s.headers.update(
        {'Content-type': 'application/json',
         'x-auth-token': auth_token})

    try:
        r = s.get('%s/volumes' % VOLUME_ENDPOINT,
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


def main(args):
    auth_ref = get_auth_ref()
    check(auth_ref, args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check neutron agents')
    parser.add_argument('ip',
                        type=IPv4Address,
                        help='neutron service IP address.')
    args = parser.parse_args()
    main(args)
