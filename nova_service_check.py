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
        service_is_up = True
        if service.status == 'enabled' and service.state == 'down':
            service_is_up = False
        metric_bool('%s_on_host_%s' %
                    (service.binary, service.host),
                    service_is_up)


def main(args):
    check(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check nova services')
    parser.add_argument('ip',
                        type=IPv4Address,
                        help='nova API IP address')
    args = parser.parse_args()
    main(args)
