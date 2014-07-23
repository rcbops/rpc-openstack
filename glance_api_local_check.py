#!/usr/bin/env python

from glanceclient import Client, exc
from keystoneclient.v2_0 import client
from keystoneclient.openstack.common.apiclient import exceptions
import maas_common
import sys

OS_IMAGE_ENDPOINT = 'http://127.0.0.1:9292'

def check(auth_details, os_auth_token, tries):
    if tries < 3:
        tries += 1
        glance = Client('1', endpoint=OS_IMAGE_ENDPOINT, token=os_auth_token)

        try:
            # We don't want to be pulling massive lists of images every time we run
            image = glance.images.list(limit=1)
            # Exceptions are only thrown when we iterate over image
            [i.id for i in image]
        except exc.HTTPUnauthorized as e:
            check(auth_details, os_auth_token, tries)
        except (exc.CommunicationError,
                exc.HTTPInternalServerError,
                exc.HTTPUnauthorized) as e:
            print "status err %s" % e
            sys.exit(1)
        else:
            print 'status OK'
            print 'metric glance_api_local_status uint32 1'


def main():
    auth_details = maas_common.set_auth_details()
    os_auth_token = maas_common.get_token_from_file(auth_details)
    check(auth_details, os_auth_token, 0)


if __name__ == "__main__":
    main()
