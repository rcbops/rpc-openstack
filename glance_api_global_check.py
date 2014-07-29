#!/usr/bin/env python

from maas_common import (get_auth_ref, get_keystone_client, get_glance_client,
                         status_err, status_ok, metric)
import sys


def check(auth_ref):
    keystone = get_keystone_client(auth_ref)
    if keystone is None:
        status_err('Unable to obtain valid keystone client, cannot proceed')

    service = keystone.services.find(type="image")
    endpoint = keystone.endpoints.find(service_id=service.id)
    os_image_endpoint = endpoint.publicurl
    os_auth_token = keystone.auth_ref['token']['id']

    glance = get_glance_client(os_auth_token, os_image_endpoint)
    if glance is None:
        status_err('Unable to obtain valid glance client, cannot proceed')

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
        status_err(e)

    status_ok()
    metric('glance_active_images', 'uint32', active)
    metric('glance_queued_images', 'uint32', queued)
    metric('glance_killed_images', 'uint32', killed)


def main():
    auth_ref = get_auth_ref()
    check(auth_ref)

if __name__ == "__main__":
    main()
