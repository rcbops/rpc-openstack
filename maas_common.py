#!/usr/bin/env python

import re
import sys

AUTH_DETAILS = {'OS_USERNAME': None,
                'OS_PASSWORD': None,
                'OS_TENANT_NAME': None,
                'OS_AUTH_URL': None}

OPENRC = '/root/openrc'


def set_auth_details():
    auth_details = AUTH_DETAILS
    pattern = re.compile('^(export\s)?(?P<key>\w+)(\s+)?=(\s+)?(?P<value>.*)$')

    openrc = open(OPENRC)
    for line in openrc:
        match = pattern.match(line)
        if match:
            k = match.group('key')
            v = match.group('value')
            if k in auth_details and auth_details[k] is None:
                auth_details[k] = v
    openrc.close()

    for key in auth_details.keys():
        if auth_details[key] is None:
            print "status err %s not set" % key
            sys.exit(1)

    return auth_details
