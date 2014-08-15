#!/usr/bin/env python

import argparse
from ipaddr import IPv4Address
from maas_common import get_neutron_client, status_err, status_ok, metric_bool


def check(args):

    NETWORK_ENDPOINT = 'http://{ip}:9696'.format(ip=args.ip)
    try:
        neutron = get_neutron_client(endpoint_url=NETWORK_ENDPOINT)

    # not gathering api status metric here so catch any exception
    except Exception as e:
        status_err(str(e))

    # gather nova service states
    agents = neutron.list_agents()['agents']

    # return all the things
    status_ok()
    for agent in agents:
        agent_is_up = True
        if agent['admin_state_up'] and not agent['alive']:
            agent_is_up = False
        metric_bool('%s_%s_on_host_%s' %
                    (agent['binary'], agent['id'], agent['host']),
                    agent_is_up)


def main(args):
    check(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check neutron agents')
    parser.add_argument('ip',
                        type=IPv4Address,
                        help='neutron API IP address')
    args = parser.parse_args()
    main(args)
