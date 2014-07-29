#!/usr/bin/env python

from maas_common import status_ok, status_err, metric
import maas_common


def check(auth_ref):

    keystone = maas_common.get_keystone_client(auth_ref=auth_ref)
    if keystone is None:
        status_err('Unable to obtain valid keystone client, cannot proceed')

    service = keystone.services.find(type="network")
    endpoints = keystone.endpoints.find(service_id=service.id)
    endpoint_url = endpoints.publicurl
    token = keystone.auth_ref['token']['id']

    neutron = maas_common.get_neutron_client(token, endpoint_url)
    if neutron is None:
        status_err('Unable to obtain valid neutron client, cannot proceed')

    results = {}
    results['networks'] = len(neutron.list_networks()['networks'])
    results['agents'] = len(neutron.list_agents()['agents'])
    results['routers'] = len(neutron.list_routers()['routers'])
    results['subnets'] = len(neutron.list_subnets()['subnets'])

    status_ok()
    metric('neutron_api_global_status', 'uint32', 1)
    for k, v in results.iteritems():
        metric('neutron_%s' % k, 'uint32', v)


def main():
    auth_ref = maas_common.get_auth_ref()
    check(auth_ref)


if __name__ == "__main__":
    main()
