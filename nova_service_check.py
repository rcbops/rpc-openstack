#!/usr/bin/env python

import argparse
from ipaddr import IPv4Address
from maas_common import get_nova_client, status_err, status_ok, metric_bool


def check(args):

    COMPUTE_ENDPOINT = 'http://{ip}:8774/v3'.format(ip=args.ip)
    try:
        nova = get_nova_client(bypass_url=COMPUTE_ENDPOINT)

    # not gathering api status metric here so catch any exception
    except Exception as e:
        status_err(str(e))

    # gather nova service states
    services = nova.services.list()

    # return all the things
    status_ok()
    for service in services:
        if service.status == 'enabled' and service.state == 'down':
            metric_bool('%s on host %s'
                        % (service.binary, service.host),
                        False)
        else:
            metric_bool('%s on host %s'
                        % (service.binary, service.host),
                        True)


def main(args):
    check(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check nova services.')
    parser.add_argument('ip',
                        type=IPv4Address,
                        help='nova service IP address.')
    args = parser.parse_args()
    main(args)
