#!/usr/bin/env python

from maas_common import (get_auth_ref, get_keystone_client, get_nova_client,
                         status_err, status_ok, metric)
import collections
from novaclient.client import exceptions as exc

SERVER_STATUSES = ['ACTIVE', 'STOPPED', 'ERROR']


def check():

    try:
        nova = get_nova_client()
        server_states = [server.state for server in nova.servers.list()]
        server_results = collections.Counter(server_states)
        status_ok()
        metric_bool('nova_api_local_status', True)
    
    # print counts of the statuses we care about
        for state in SERVER_STATUSES:
            metric('nova_servers_in_state_%s' % state,
                   'uint32',
                   server_results['state'])

    except exc.ClientException:
        metric_bool('nova_api_local_status', False)
    except Exception as e:
        status_err(str(e))



def main():
    check()

if __name__ == "__main__":
    main()
