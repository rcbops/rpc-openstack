#!/usr/bin/env python

from maas_common import (status_ok, status_err, metric, metric_bool,
                         get_keystone_client, get_auth_ref)
import argparse
from ipaddr import IPv4Address
import requests
from requests import exceptions as exc


def check(args):
    headers = {'Content-type': 'application/json'}
    path_options = {}
    if args.auth:
        auth_ref = get_auth_ref()
        keystone = get_keystone_client(auth_ref)
        auth_token = keystone.auth_token
        tenant_id = keystone.tenant_id
        headers['auth_token'] = auth_token
        path_options['tenant_id'] = tenant_id

    scheme = args.ssl and 'https' or 'http'
    endpoint = '{scheme}://{ip}:{port}'.format(ip=args.ip, port=args.port,
                                               scheme=scheme)
    if args.version is not None:
        path_options['version'] = args.version
    path = args.path.format(path_options)

    s = requests.Session()

    s.headers.update(headers)

    if path and not path.startswith('/'):
        url = '/'.join((endpoint, path))
    else:
        url = ''.join((endpoint, path))
    try:
        r = s.get(url, verify=False, timeout=10)
    except (exc.ConnectionError,
            exc.HTTPError,
            exc.Timeout):
        up = False
    else:
        up = True

    status_ok()
    metric_bool('{name}_api_local_status'.format(name=args.name), up)

    if up and r.ok:
        milliseconds = r.elapsed.total_seconds() * 1000
        metric('{name}_api_local_response_time'.format(name=args.name),
               'uint32',
               '%.3f' % milliseconds,
               'ms')


def main(args):
    check(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check service is up.')
    parser.add_argument('name', help='Service name.')
    parser.add_argument('ip', type=IPv4Address, help='Service IP address.')
    parser.add_argument('port', type=int, help='Service port.')
    parser.add_argument('--path', default='',
                        help='Service API path, this should include '
                             'placeholders for the version "{version}" and '
                             'tenant ID "{tenant_id}" if required.')
    parser.add_argument('--auth', action='store_true', default=False,
                        help='Does this API check require auth?')
    parser.add_argument('--ssl', action='store_true', default=False,
                        help='Should SSL be used.')
    parser.add_argument('--version', help='Service API version.')
    args = parser.parse_args()
    main(args)
