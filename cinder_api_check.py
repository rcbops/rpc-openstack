#!/usr/bin/env python
import os
import sys
from cinderclient.client import Client
from cinderclient import exceptions as exc
from maas_common import get_auth_details


def main():
    auth_details = get_auth_details()

    try:
        cinder = Client('1',
                        auth_details['OS_USERNAME'],
                        auth_details['OS_PASSWORD'],
                        auth_details['OS_TENANT_NAME'],
                        auth_details['OS_AUTH_URL'])
    except (exc.Unauthorized, exc.AuthorizationFailure) as e:
        print "status err %s" % e
        sys.exit(1)

    volumes = cinder.volumes.list()
    available = [v for v in volumes if v.status == 'available']
    errored = [v for v in volumes if v.status == 'error' or
               v.status == 'error-deleting']
    size = sum([v.size for v in available])

    snapshots = cinder.volume_snapshots.list()
    snapshots_available = [v for v in snapshots if v.status == 'available']
    snapshots_errored = [v for v in snapshots if v.status == 'error' or
               v.status == 'error-deleting']
    snapshots_size = sum([v.size for v in snapshots_available])

    print 'status OK'
    print 'metric cinder_volumes uint32 %d' % len(volumes)
    print 'metric cinder_volumes_available uint32 %d' % len(available)
    print 'metric cinder_volumes_errored uint32 %d' % len(errored)
    print 'metric cinder_volumes_size uint32 %d' % size
    print 'metric cinder_volume_snapshots uint32 %d' % len(snapshots)
    print 'metric cinder_volume_snapshots_available uint32 %d' % len(snapshots_available)
    print 'metric cinder_volume_snapshots_errored uint32 %d' % len(snapshots_errored)
    print 'metric cinder_volume_snapshots_size uint32 %d' % snapshots_size

if __name__ == "__main__":
    main()
