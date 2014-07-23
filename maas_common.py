#!/usr/bin/env python

import os
import sys

# We can set these here to avoid looking in os.environ
AUTH_DETAILS = {'OS_USERNAME': None,
                'OS_PASSWORD': None,
                'OS_TENANT_NAME': None,
                'OS_AUTH_URL': None}


def set_auth_details():
    auth_details = AUTH_DETAILS

    for key in auth_details.keys():
        if AUTH_DETAILS[key] is None:
            if key in os.environ:
                auth_details[key] = os.environ[key]
            else:
                print "status err os.environ['%s'] not set" % key
                sys.exit(1)

    return auth_details
