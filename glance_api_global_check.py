#!/usr/bin/env python

from glanceclient import exc
from maas_common import (get_auth_ref, get_keystone_client, get_glance_client,
                         status_err, status_ok, metric, metric_bool)
import sys


def check():
    try:
        glance = get_glance_client()
        active, queued, killed = 0, 0, 0

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

        status_ok()
        metric_bool('glance_api_global_status', True)
        metric('glance_active_images', 'uint32', active)
        metric('glance_queued_images', 'uint32', queued)
        metric('glance_killed_images', 'uint32', killed)
    except exc.HTTPException:
        status_ok()
        metric_bool('glance_api_global_status', False)
    except Exception as e:
        status_err(str(e))


def main():
    check()

if __name__ == "__main__":
    main()
