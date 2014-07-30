#!/usr/bin/env python

from maas_common import (get_auth_ref, get_keystone_client, get_nova_client,
                         status_err, status_ok, metric)
import collections

SERVER_STATUSES = ['ACTIVE', 'STOPPED', 'ERROR']


def check(auth_ref):

    nova = get_nova_client()
    if nova is None:
        status_err('Unable to obtain valid nova client, cannot proceed')

    try:
        server_states = [server.state for server in nova.servers.list()]
        server_results = collections.Counter(server_states)

    except Exception as e:
        status_err(str(e))

    status_ok()
    # print counts of the statuses we care about
    for state in SERVER_STATUSES:
            metric('nova_servers_in_state_%s' % state,
                   'uint32',
                   server_results['state'])


def main():
    auth_ref = get_auth_ref()
    check(auth_ref)

if __name__ == "__main__":
    main()
