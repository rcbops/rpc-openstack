#!/usr/bin/env python
import os
import sys
from cinderclient.client import Client
from cinderclient import exceptions as exc


def set_auth_details():
    auth_details = {'OS_USERNAME': None,
                    'OS_PASSWORD': None,
                    'OS_TENANT_NAME': None,
                    'OS_AUTH_URL': None}

    for key in auth_details.keys():
        if key in os.environ:
            auth_details[key] = os.environ[key]

    return auth_details


def main():
    auth_details = set_auth_details()

    for key, value in auth_details.items():
        if value is None:
            print "status err os.environ['%s'] not set" % key
            sys.exit(1)

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
    errored = [v for v in volumes if v.status == 'error']
    size = sum([v.size for v in available])

    print 'status OK'
    print 'metric cinder_volumes uint32 %d' % len(volumes)
    print 'metric cinder_errored uint32 %d' % len(errored)
    print 'metric cinder_size uint32 %d' % size
    
if __name__ == "__main__":
    main()
