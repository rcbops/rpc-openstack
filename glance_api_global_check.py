#!/usr/bin/env python

from glanceclient import Client, exc
from keystoneclient.v2_0 import client
from keystoneclient.openstack.common.apiclient import exceptions
import maas_common
import sys


def main():
    auth_details = maas_common.set_auth_details()

    try:
        keystone = client.Client(username=auth_details['OS_USERNAME'],
                                 password=auth_details['OS_PASSWORD'],
                                 tenant_name=auth_details['OS_TENANT_NAME'],
                                 auth_url=auth_details['OS_AUTH_URL'])
    except (exceptions.Unauthorized, exceptions.AuthorizationFailure) as e:
        print "status err %s" % e
        sys.exit(1)

    service = keystone.services.find(type="image")
    endpoint = keystone.endpoints.find(service_id=service.id)
    os_image_endpoint = endpoint.publicurl
    os_auth_token = keystone.auth_ref['token']['id']

    glance = Client('1', endpoint=os_image_endpoint, token=os_auth_token)

    active, queued, killed = 0, 0, 0

    try:
        images = glance.images.list()
        # We can only iterate over images once since it's using pagination
        for i in images:
            if i.status == "active":
                active += 1
            if i.status == "queued":
                queued += 1
            if i.status == "killed":
                killed += 1
    except (exc.CommunicationError,
            exc.HTTPInternalServerError,
            exc.HTTPUnauthorized) as e:
        print "status err %s" % e
        sys.exit(1)

    print 'status OK'
    print 'metric glance_active_images uint32 %d' % active
    print 'metric glance_queued_images uint32 %d' % queued
    print 'metric glance_killed_images uint32 %d' % killed

if __name__ == "__main__":
    main()
