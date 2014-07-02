#!/usr/bin/env python

import requests
import sys

OVERVIEW_URL = "http://localhost:15672/api/overview"
NODES_URL = "http://localhost:15672/api/nodes"
USERNAME = 'guest'
PASSWORD = 'guest'
CLUSTERED = True
CLUSTER_SIZE = 3

OVERVIEW_METRICS = {"queue_totals": ("messages",
                                     "messages_ready",
                                     "messages_unacknowledged"),
                    "message_stats": ("get",
                                      "ack",
                                      "deliver_get",
                                      "deliver",
                                      "publish")}
NODES_METRICS = ("proc_used",
                 "proc_total",
                 "fd_used",
                 "fd_total",
                 "sockets_used",
                 "sockets_total",
                 "mem_used",
                 "mem_limit",
                 "mem_alarm",
                 "disk_free_alarm",
                 "uptime")


def main():
    metrics = {}

    try:
        r = requests.get(OVERVIEW_URL, auth=(USERNAME, PASSWORD))
    except requests.exceptions.ConnectionError:
        error()

    if r.status_code == 200:
        for k in OVERVIEW_METRICS.keys():
            if k in r.json():
                for i in OVERVIEW_METRICS[k]:
                    if i in r.json()[k]:
                        metrics[i] = r.json()[k][i]
    else:
        error()

    try:
        r = requests.get(NODES_URL, auth=(USERNAME, PASSWORD))
    except requests.exceptions.ConnectionError:
        error()

    if r.status_code == 200:
        for i in NODES_METRICS:
            if i in r.json()[0]:
                metrics[i] = r.json()[0][i]
    else:
        error()

    if CLUSTERED and len(r.json()) < CLUSTER_SIZE:
      print "status err cluster too small"
    else:
      print "status ok"

    for k in metrics.keys():
        print "metric %s int64 %d" % (k, metrics[k])


def error():
    print "status error"
    sys.exit(1)


if __name__ == "__main__":
    main()