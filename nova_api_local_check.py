#!/usr/bin/env python

import argparse
import collections
from time import time
from ipaddr import IPv4Address
from maas_common import (get_nova_client, status_err, metric,
                         status_ok, metric_bool)
from novaclient.client import exceptions as exc

SERVER_STATUSES = ['ACTIVE', 'STOPPED', 'ERROR']

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

        # gather some metrics
        status_count = collections.Counter([s.status for s in nova.servers.list()])
        

    status_ok()
    metric_bool('nova_api_local_status', is_up)
    # only want to send other metrics if api is up
    if is_up:
        metric('nova_api_local_response_time',
               'uint32',
               '%.3f' % milliseconds,
               'ms')
        for status in SERVER_STATUSES:
            metric('nova_servers_in_state_%s' % status,
                   'uint32',
                   status_count[status])


def main(args):
    check(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check nova API')
    parser.add_argument('ip',
                        type=IPv4Address,
                        help='nova API IP address')
    args = parser.parse_args()
    main(args)
