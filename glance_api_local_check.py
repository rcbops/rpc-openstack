#!/usr/bin/env python

from glanceclient import Client, exc
import maas_common
import sys

OS_IMAGE_ENDPOINT = 'http://127.0.0.1:9292'


def check(os_auth_token, tries=0):
    if tries >= 3:
        return

    glance = Client('1', endpoint=OS_IMAGE_ENDPOINT, token=os_auth_token)

    try:
        # We don't want to be pulling massive lists of images every time we
        # run
        image = glance.images.list(limit=1)
        # Exceptions are only thrown when we iterate over image
        [i.id for i in image]
    except exc.HTTPUnauthorized as e:
        check(os_auth_token, tries + 1)
    except (exc.CommunicationError,
            exc.HTTPInternalServerError,
            exc.HTTPUnauthorized) as e:
        print "status err %s" % e
        sys.exit(1)
    else:
        print 'status OK'
        print 'metric glance_api_local_status uint32 1'


def main():
    auth_ref = maas_common.get_auth_ref()
    os_auth_token = auth_ref['token']['id']
    check(os_auth_token)


if __name__ == "__main__":
    main()
