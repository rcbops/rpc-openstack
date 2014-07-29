#!/usr/bin/env python

import memcache

from maas_common import status_ok, status_err, metric

MEMCACHE_KEYS = ("get_hits",
                 "get_misses")


def main():
    metrics = {}
    mc = memcache.Client(['localhost:11211'], debug=0)

    if len(mc.get_stats()) == 0:
        status_err()

    stats = mc.get_stats()[0][1]

    for k in MEMCACHE_KEYS:
        if k in stats:
            metrics[k] = stats[k]

    if len(metrics.keys()) > 0:
        status_ok()
        for k, v in metrics.items():
            metric(k, 'int64', v)
    else:
        status_err()


if __name__ == "__main__":
    main()
