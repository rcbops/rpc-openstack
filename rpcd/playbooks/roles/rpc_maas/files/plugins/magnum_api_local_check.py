#!/usr/bin/env python

# Copyright 2017, Rackspace US, Inc.
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
import time

import ipaddr
from maas_common import get_auth_ref
from maas_common import get_magnum_client
from maas_common import metric
from maas_common import metric_bool
from maas_common import print_output
from maas_common import status_err
from maas_common import status_ok
from magnumclient.common.apiclient import exceptions as exc


def check(auth_ref, args):
    MAGNUM_ENDPOINT = 'http://{ip}:9511/v1'.format(ip=args.ip,)

    try:
        if args.ip:
            magnum = get_magnum_client(endpoint=MAGNUM_ENDPOINT)
        else:
            magnum = get_magnum_client()

        api_is_up = True
    except exc.HttpError as e:
        api_is_up = False
    # Any other exception presumably isn't an API error
    except Exception as e:
        status_err(str(e))
    else:
        # time something arbitrary
        start = time.time()
        magnum.cluster_templates.list()
        end = time.time()
        milliseconds = (end - start) * 1000

    status_ok()
    metric_bool('magnum_api_local_status', api_is_up)
    if api_is_up:
        # only want to send other metrics if api is up
        metric('magnum_api_local_response_time',
               'double',
               '%.3f' % milliseconds,
               'ms')


def main(args):
    auth_ref = get_auth_ref()
    check(auth_ref, args)


if __name__ == "__main__":
    with print_output():
        parser = argparse.ArgumentParser(
            description='Check Magnum API against local or remote address')
        parser.add_argument('ip', nargs='?', type=ipaddr.IPv4Address,
                            help="Check Magnum API against "
                            " local or remote address")
        args = parser.parse_args()
        main(args)
