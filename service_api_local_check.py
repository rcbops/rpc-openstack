#!/usr/bin/env python

from maas_common import (status_ok, status_err, metric, metric_bool,
                         get_keystone_client, get_auth_ref)
import argparse
import requests
from requests import exceptions as exc


def check(auth_ref, args):

    keystone = get_keystone_client(auth_ref)
    auth_token = keystone.auth_token
    tenant_id = keystone.tenant_id

    scheme = args.ssl and 'https' or 'http'
    endpoint = '{scheme}://{ip}:{port}'.format(ip=args.ip, port=args.port,
                                               scheme=scheme)
    path_options = {'tenant_id': tenant_id}
    try:
        path_options['version'] = args.version
    except AttributeError:
        pass
    path = args.path.format(path_options)

    s = requests.Session()

    s.headers.update(
        {'Content-type': 'application/json',
         'x-auth-token': auth_token})

    try:
        r = s.get('/'.join((endpoint, path)),
                  verify=False,
                  timeout=10)
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
        metric('{name}_api_response_time'.format(name=args.name),
               'uint32',
               milliseconds,
               'milliseconds')


def main(args):
    auth_ref = get_auth_ref()
    check(auth_ref, args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check service is up.')
    parser.add_argument('name', help='Service name.')
    parser.add_argument('ip', help='Service IP address.')
    parser.add_argument('port', help='Service port.')
    parser.add_argument('path',
                        help='Service API path, this should include '
                             'placeholders for the version "{version}" and '
                             'tenant ID "{tenant_id}" if required.')
    parser.add_argument('ssl', type=bool, help='Should SSL be used.')
    parser.add_argument('--version', help='Service API version.')
    args = parser.parse_args()
    main(args)
