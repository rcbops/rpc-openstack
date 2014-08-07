#!/usr/bin/env python

import argparse
from time import time
from ipaddr import IPv4Address
from maas_common import (get_neutron_client, metric,
                         status_err, status_ok, metric_bool)
from neutronclient.client import exceptions as exc


def check(args):

    NETWORK_ENDPOINT = 'http://{ip}:9696'.format(ip=args.ip)

    try:
        neutron = get_neutron_client(endpoint_url=NETWORK_ENDPOINT)
        is_up = True
    # if we get a NeutronClientException don't bother sending any other metric
    # The API IS DOWN
    except exc.NeutronClientException:
        is_up = False
    # Any other exception presumably isn't an API error
    except Exception as e:
        status_err(str(e))
    else:
        # time something arbitrary
        start = time()
        neutron.list_agents()
        end = time()
        milliseconds = (end - start) * 1000

    status_ok()
    metric_bool('neutron_api_local_status', is_up)
    # only want to send other metrics if api is up
    if is_up:
        metric('neutron_api_local_response_time', 
               'uint32',
               '%.3f' % milliseconds,
               'ms')


def main(args):
    check(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check neutron agents')
    parser.add_argument('ip',
                        type=IPv4Address,
                        help='neutron service IP address.')
    args = parser.parse_args()
    main(args)
