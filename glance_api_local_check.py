#!/usr/bin/env python

import argparse
import collections
from ipaddr import IPv4Address
from maas_common import (status_ok, status_err, metric, metric_bool,
                         get_keystone_client, get_auth_ref)
from requests import Session
from requests import exceptions as exc

IMAGE_STATUSES = ['active', 'queued', 'killed']


def check(auth_ref, args):
    # We call get_keystone_client here as there is some logic within to get a
    # new token if previous one is bad.
    keystone = get_keystone_client(auth_ref)
    auth_token = keystone.auth_token
    api_endpoint = 'http://{ip}:9292/v1'.format(ip=args.ip)

    s = Session()

    s.headers.update(
        {'Content-type': 'application/json',
         'x-auth-token': auth_token})

    try:
        # Hit something that isn't querying the glance-registry, since we
        # query glance-registry in separate checks
        r = s.get('%s/' % api_endpoint, verify=False,
                  timeout=10)
        milliseconds = r.elapsed.total_seconds() * 1000
        is_up = r.ok
    except (exc.ConnectionError, exc.HTTPError, exc.Timeout):
        is_up = False
    except Exception as e:
        status_err(str(e))
    else:
        # gather some metrics to report
        try:
            r = s.get('%s/images/detail' % api_endpoint, verify=False,
                      timeout=10)
        except Exception as e:
            status_err(str(e))
        else:
            image_statuses = [i['status'] for i in r.json()['images']]
            status_count = collections.Counter(image_statuses)

    status_ok()
    metric_bool('glance_api_local_status', is_up)

    # only want to send other metrics if api is up
    if is_up:
        metric('glance_api_local_response_time',
               'uint32',
               '%.3f' % milliseconds,
               'ms')
        for status in IMAGE_STATUSES:
            metric('glance_%s_images' % status, 'uint32', status_count[status])


def main(args):
    auth_ref = get_auth_ref()
    check(auth_ref, args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check glance API')
    parser.add_argument('ip',
                        type=IPv4Address,
                        help='glance API IP address')
    args = parser.parse_args()
    main(args)
