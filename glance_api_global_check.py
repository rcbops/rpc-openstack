#!/usr/bin/env python

from glanceclient import exc
from maas_common import (get_auth_ref, get_keystone_client, get_glance_client,
                         status_err, status_ok, metric, metric_bool)
import collections
import sys

IMAGE_STATUSES = ['active', 'queued', 'killed']


def check():
    try:
        glance = get_glance_client()

        counter = collections.Counter([i.status for i in glance.images.list()])

        status_ok()
        metric_bool('glance_api_global_status', True)

        for status in IMAGE_STATUSES:
            # Only send metrics for statuses that we care about -- seeing
            # deleted count over time is probably not useful.
            metric('glance_%s_images' % status, 'uint32', counter[status])
    except exc.HTTPException:
        status_ok()
        metric_bool('glance_api_global_status', False)
    except Exception as e:
        status_err(str(e))


def main():
    check()

if __name__ == "__main__":
    main()
