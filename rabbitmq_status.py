#!/usr/bin/env python

import requests
import subprocess

from maas_common import metric, status_ok, status_err

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


def hostname():
    """Return the name of the current host/node."""
    return subprocess.check_output(['hostname']).strip()


def main():
    metrics = {}
    s = requests.Session()  # Make a Session to store the authenticate creds
    s.auth = (USERNAME, PASSWORD)

    try:
        r = s.get(OVERVIEW_URL)
    except requests.exceptions.ConnectionError as e:
        status_err(str(e))

    if r.ok:
        resp_json = r.json()  # Parse the JSON once
        for k in OVERVIEW_METRICS:
            if k in resp_json:
                for i in OVERVIEW_METRICS[k]:
                    if i in resp_json[k]:
                        metrics[i] = resp_json[k][i]
    else:
        status_err('Received status {0} from RabbitMQ API'.format(
            r.status_code))

    try:
        r = s.get(NODES_URL)
    except requests.exceptions.ConnectionError as e:
        status_err(str(e))

    name = hostname()
    is_cluster_member = False
    if r.ok:
        resp_json = r.json()
        for i in NODES_METRICS:
            if i in resp_json[0]:
                metrics[i] = resp_json[0][i]

        # Ensure this node is a member of the cluster
        is_cluster_member = any(name == n['name'] for n in resp_json)
        # Gather the queue lengths for all nodes in the cluster
        queues = [n['run_queue'] for n in resp_json]
        # Grab the first queue length
        first = queues.pop()
        # Check that all other queues are equal to it
        if not all(first == q for q in queues):
            # If they're not, the queues are not synchronized
            print "status err cluster not replicated across all nodes"
    else:
        status_err('Received status {0} from RabbitMQ API'.format(
            r.status_code))

    if CLUSTERED:
        if len(r.json()) < CLUSTER_SIZE:
            status_err('cluster too small')
        if not is_cluster_member:
            status_err('{0} not a member of the cluster'.format(name))
    else:
        status_ok()

    for k, v in metrics.items():
        metric(k, 'int64', v)


if __name__ == "__main__":
    main()
