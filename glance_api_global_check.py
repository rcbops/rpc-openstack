#!/usr/bin/env python

import maas_common
import sys


def check(auth_ref):
    keystone = maas_common.get_keystone_client(auth_ref)
    if keystone is None:
        print 'status err Unable to obtain valid keystone client, ' \
              'cannot proceed'
        sys.exit(1)

    service = keystone.services.find(type="image")
    endpoint = keystone.endpoints.find(service_id=service.id)
    os_image_endpoint = endpoint.publicurl
    os_auth_token = keystone.auth_ref['token']['id']

    glance = maas_common.get_glance_client(os_auth_token, os_image_endpoint)
    if glance is None:
        print 'status err Unable to obtain valid glance client, ' \
              'cannot proceed'
        sys.exit(1)

    active, queued, killed = 0, 0, 0

    try:
        images = glance.images.list()
        # We can only iterate over images once since it's using
        # pagination
        for i in images:
            if i.status == "active":
                active += 1
            if i.status == "queued":
                queued += 1
            if i.status == "killed":
                killed += 1
    except Exception as e:
        print "status err %s" % e
        sys.exit(1)

    print 'status OK'
    print 'metric glance_active_images uint32 %d' % active
    print 'metric glance_queued_images uint32 %d' % queued
    print 'metric glance_killed_images uint32 %d' % killed


def main():
    auth_ref = maas_common.get_auth_ref()
    check(auth_ref)

if __name__ == "__main__":
    main()
