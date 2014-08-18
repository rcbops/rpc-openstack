#!/usr/bin/env python

import re
import argparse
import memcache
from ipaddr import IPv4Address

from maas_common import status_ok, status_err, metric, metric_bool


VERSION_RE = re.compile('STAT version (\d+\.\d+\.\d+)(?![-+0-9\\.])')
VERSION = '1.4.14 (Ubuntu)'
MEMCACHE_METRICS = ['total_items',
                    'get_hits',
                    'get_misses',
                    'total_connections']


def item_stats(host, port):
    """Check the stats for items and connection status."""

    mc = memcache.Client(['%s:%s' % (host, port)])
    stats = mc.get_stats()[0][1]
    if not stats:
        status_err('could not retrieve status from memcached')
    return stats


def main(args):

    bind_ip = str(args.ip)
    port = args.port

    stats = item_stats(bind_ip, port)

    if stats['version'] != VERSION:
        status_err('This plugin has only been tested with version %s '
                   'of memcached, and you are using version %s'
                   % (VERSION, current_version))

    if stats is not None:
        status_ok
        metric_bool('memcache_api_local_status', True)
        for m in MEMCACHE_METRICS:
            metric('memcache_%s' % m, 'uint64', stats[m])
    else:
        status_err('memcached is unreachable')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check glance API')
    parser.add_argument('ip', type=IPv4Address, help='memcached IP address.')
    parser.add_argument('--port', type=int,
                        default=11211, help='memcached port.')
    args = parser.parse_args()
    main(args)
