#!/usr/bin/env python

from maas_common import (status_ok, status_err, metric, metric_bool,
                         get_neutron_client)
from neutronclient.common import exceptions as exc


def check():

    try:
        neutron = get_neutron_client()

        networks = len(neutron.list_networks()['networks'])
        agents = len(neutron.list_agents()['agents'])
        routers = len(neutron.list_routers()['routers'])
        subnets = len(neutron.list_subnets()['subnets'])

        status_ok()
        metric_bool('neutron_api_global_status', True)
        metric('neutron_networks', 'uint32', networks)
        metric('neutron_agents', 'uint32', agents)
        metric('neutron_routers', 'uint32', routers)
        metric('neutron_subnets', 'uint32', subnets)

    # if we get a NeutronClientException don't bother sending any other metric
    # The API IS DOWN
    except exc.NeutronClientException:
        metric_bool('nova_api_local_status', False)
    # Any other exception presumably isn't an API error
    except Exception as e:
        status_err(str(e))


def main():
    check()


if __name__ == "__main__":
    main()
