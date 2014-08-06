#!/usr/bin/env python

import argparse
from ipaddr import IPv4Address
from maas_common import (get_neutron_client,
                         status_err, status_ok, metric_bool)
from neutronclient.client import exceptions as exc


def check(args):

    NETWORK_ENDPOINT = 'http://{ip}:9696'.format(ip=args.ip)

    try:
        get_neutron_client(endpoint_url=NETWORK_ENDPOINT)
        status_ok()
        metric_bool('neutron_api_local_status', True)

    # if we get a NeutronClientException don't bother sending any other metric
    # The API IS DOWN
    except exc.NeutronClientException:
        status_ok()
        metric_bool('neutron_api_local_status', False)
    # Any other exception presumably isn't an API error
    except Exception as e:
        status_err(str(e))


def main(args):
    check(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check neutron agents')
    parser.add_argument('ip',
                        type=IPv4Address,
                        help='neutron service IP address.')
    args = parser.parse_args()
    main(args)
