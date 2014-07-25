#!/usr/bin/env python

import maas_common
import sys


def check(auth_ref):

    keystone = maas_common.get_keystone_client(auth_ref=auth_ref)
    if keystone is None:
        print 'status err Unable to obtain valid keystone client, ' \
              'cannot proceed'
        sys.exit(1)

    service = keystone.services.find(type="network")
    endpoints = keystone.endpoints.find(service_id=service.id)
    endpoint_url = endpoints.publicurl
    token = keystone.auth_ref['token']['id']

    neutron = maas_common.get_neutron_client(token, endpoint_url)
    if neutron is None:
        print 'status err Unable to obtain valid neutron client, ' \
              'cannot proceed'
        sys.exit(1)

    networks = len(neutron.list_networks()['networks'])
    agents = len(neutron.list_agents()['agents'])
    routers = len(neutron.list_routers()['routers'])
    subnets = len(neutron.list_subnets()['subnets'])

    print 'status OK'
    print 'metric neutron_api_global_status uint32 1'
    print 'metric neutron_routers uint32 %s' % routers
    print 'metric neutron_networks uint32 %s' % networks
    print 'metric neutron_subnets uint32 %s' % subnets
    print 'metric neutron_agents uint32 %s' % agents


def main():
    auth_ref = maas_common.get_auth_ref()
    check(auth_ref)


if __name__ == "__main__":
    main()
