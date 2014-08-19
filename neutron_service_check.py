#!/usr/bin/env python

# Copyright 2014, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
