#!/usr/bin/env python

from glanceclient import Client, exc
from keystoneclient.v2_0 import client
from keystoneclient.openstack.common.apiclient import exceptions
import maas_common
import os
import sys

OS_IMAGE_ENDPOINT = 'http://127.0.0.1:9292'


def main():
    auth_details = maas_common.set_auth_details()

    for key, value in auth_details.items():
        if value is None:
            print "status err os.environ['%s'] not set" % key
            sys.exit(1)

    try:
        keystone = client.Client(username=auth_details['OS_USERNAME'],
                                 password=auth_details['OS_PASSWORD'],
                                 tenant_name=auth_details['OS_TENANT_NAME'],
                                 auth_url=auth_details['OS_AUTH_URL'])
    except (exceptions.Unauthorized, exceptions.AuthorizationFailure) as e:
        print "status err %s" % e
        sys.exit(1)

    os_auth_token = keystone.auth_ref['token']['id']

    glance = Client('1', endpoint=OS_IMAGE_ENDPOINT, token=os_auth_token)

    try:
        # We don't want to be pulling massive lists of images every time we run
        image = glance.images.list(limit=1)
        # Exceptions are only thrown when we iterate over image
        [i.id for i in image]
    except (exc.CommunicationError,
            exc.HTTPInternalServerError,
            exc.HTTPUnauthorized) as e:
        print "status err %s" % e
        sys.exit(1)

    print 'status OK'
    print 'metric glance_api_local_status uint32 1'

if __name__ == "__main__":
    main()
