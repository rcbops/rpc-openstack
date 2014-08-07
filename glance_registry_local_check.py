#!/usr/bin/env python

import argparse
from ipaddr import IPv4Address
from maas_common import (status_ok, status_err, metric, get_keystone_client,
                         get_auth_ref, metric_bool)
from requests import Session
from requests import exceptions as exc


def check(auth_ref, args):
    # We call get_keystone_client here as there is some logic within to get a
    # new token if previous one is bad.
    keystone = get_keystone_client(auth_ref)
    auth_token = keystone.auth_token
    registry_endpoint = 'http://{ip}:9191'.format(ip=args.ip)

    s = Session()

    s.headers.update(
        {'Content-type': 'application/json',
         'x-auth-token': auth_token})

    try:
        # /images returns a list of public, non-deleted images
        r = s.get('%s/images' % registry_endpoint, verify=False, timeout=10)
        is_up = r.ok
    except (exc.ConnectionError, exc.HTTPError, exc.Timeout):
        is_up = False
    except Exception as e:
        status_err(str(e))

    status_ok()
    metric_bool('glance_registry_local_status', is_up)
    # only want to send other metrics if api is up
    if is_up:
        milliseconds = r.elapsed.total_seconds() * 1000
        metric('glance_registry_local_response_time', 'uint32', milliseconds)


def main(args):
    auth_ref = get_auth_ref()
    check(auth_ref, args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check glance api')
    parser.add_argument('ip',
                        type=IPv4Address,
                        help='glance service IP address.')
    args = parser.parse_args()
    main(args)
