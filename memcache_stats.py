#!/usr/bin/env python

import memcache
import sys

MEMCACHE_KEYS = ("get_hits",
                 "get_misses")


def main():
    metrics = {}
    mc = memcache.Client(['localhost:11211'], debug=0)

    if len(mc.get_stats()) == 0:
        error()

    stats = mc.get_stats()[0][1]

    for k in MEMCACHE_KEYS:
        if k in stats:
            metrics[k] = stats[k]

    if len(metrics.keys()) > 0:
        print "status ok"
        for k in metrics.keys():
            print "metric %s int64 %s" % (k, metrics[k])
    else:
        error()


def error():
    print "status error"
    sys.exit(1)


if __name__ == "__main__":
    main()
