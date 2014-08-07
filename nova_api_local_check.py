#!/usr/bin/env python

import argparse
from time import time
from ipaddr import IPv4Address
from maas_common import (get_nova_client, status_err, metric,
                         status_ok, metric_bool)
from novaclient.client import exceptions as exc


def check(args):

    COMPUTE_ENDPOINT = 'http://{ip}:8774/v3'.format(ip=args.ip)

    try:
        nova = get_nova_client(bypass_url=COMPUTE_ENDPOINT)
        is_up = True
    except exc.ClientException:
        is_up = False
    # Any other exception presumably isn't an API error
    except Exception as e:
        status_err(str(e))
    else:
        # time something arbitrary
        start = time()
        nova.services.list()
        end = time()
        milliseconds = (end - start) * 1000

    status_ok()
    metric_bool('nova_api_local_status', is_up)
    # only want to send other metrics if api is up
    if is_up:
        metric('nova_api_local_response_time', 'uint32', milliseconds)


def main(args):
    check(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check nova services.')
    parser.add_argument('ip',
                        type=IPv4Address,
                        help='nova service IP address.')
    args = parser.parse_args()
    main(args)
