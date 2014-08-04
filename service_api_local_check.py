#!/usr/bin/env python

from maas_common import (status_ok, status_err, metric, metric_bool,
                         get_keystone_client, get_auth_ref)
import argparse
import requests
from requests import exceptions as exc


def check(auth_ref, args):

    keystone = get_keystone_client(auth_ref)
    auth_token = keystone.auth_token
    scheme = args.ssl and 'https' or 'http'
    endpoint = '{scheme}://{ip}:{port}'.format(ip=args.ip, port=args.port,
                                               scheme=scheme)

    s = requests.Session()

    s.headers.update(
        {'Content-type': 'application/json',
         'x-auth-token': auth_token})

    try:
        r = s.get('/'.join((endpoint, args.path)),
                  verify=False,
                  timeout=10)
    except (exc.ConnectionError,
            exc.HTTPError,
            exc.Timeout):
        up = False
    else:
        up = True

    status_ok()
    metric_bool('%s_api_local_status' % args.name, up)

    if up and r.ok:
        milliseconds = r.elapsed.total_seconds() * 1000
        metric('%s_api_response_time' % args.name, 'uint32', milliseconds)


def main(args):
    auth_ref = get_auth_ref()
    check(auth_ref, args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check service in up.')
    parser.add_argument('name', help='Service name.')
    parser.add_argument('ip', help='Service IP address.')
    parser.add_argument('port', help='Service port.')
    parser.add_argument('path', help='Service API request, this should include'
                                     'the version and tenant ID if required.')
    parser.add_argument('ssl', type=bool, help='http or https.')
    args = parser.parse_args()
    main(args)
