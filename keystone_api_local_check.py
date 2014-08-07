#!/usr/bin/env python

import argparse
from time import time
from ipaddr import IPv4Address
from maas_common import (get_keystone_client, status_err, status_ok, metric,
                         metric_bool)
from keystoneclient.openstack.common.apiclient import exceptions as exc


def check(args):

    IDENTITY_ENDPOINT = 'http://{ip}:35357/v2.0'.format(ip=args.ip)

    try:
        keystone = get_keystone_client(endpoint=IDENTITY_ENDPOINT)
        is_up = True
    except (exc.HttpServerError, exc.ClientException):
        is_up = False
    # Any other exception presumably isn't an API error
    except Exception as e:
        status_err(str(e))
    else:
        # time something arbitrary
        start = time()
        keystone.services.list()
        end = time()
        milliseconds = (end - start) * 1000

    status_ok()
    metric_bool('keystone_api_local_status', is_up)
    # only want to send other metrics if api is up
    if is_up:
        metric('keystone_api_local_response_time',
               'uint32',
               '%.3f' % milliseconds,
               'ms')


def main(args):
    check(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check keystone API')
    parser.add_argument('ip',
                        type=IPv4Address,
                        help='nova API IP address.')
    args = parser.parse_args()
    main(args)
