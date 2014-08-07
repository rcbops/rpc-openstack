#!/usr/bin/env python

import argparse
from time import time
from ipaddr import IPv4Address
from maas_common import (get_auth_ref, get_heat_client, metric_bool,
                         metric, status_ok, status_err)
from heatclient import exc


def check(args, tenant_id):

    HEAT_ENDPOINT = ('http://{ip}:8004/v1/{tenant}'.format
                     (ip=args.ip, tenant=tenant_id))

    try:
        heat = get_heat_client(endpoint=HEAT_ENDPOINT)
        is_up = True
    except exc.HTTPException as e:
        is_up = False
    # Any other exception presumably isn't an API error
    except Exception as e:
        status_err(str(e))
    else:
        # time something arbitrary
        start = time()
        heat.build_info.build_info()
        end = time()
        milliseconds = (end - start) * 1000

    status_ok()
    metric_bool('heat_api_local_status', is_up)
    if is_up:
        # only want to send other metrics if api is up
        metric('heat_api_local_response_time', 'uint32', milliseconds, 'ms')


def main(args):
    auth_ref = get_auth_ref()
    tenant_id = auth_ref['token']['tenant']['id']
    check(args, tenant_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check heat API')
    parser.add_argument('ip',
                        type=IPv4Address,
                        help='heat API IP address.')
    args = parser.parse_args()
    main(args)
