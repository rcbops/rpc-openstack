#!/usr/bin/env python

import re
import sys

AUTH_DETAILS = {'OS_USERNAME': None,
                'OS_PASSWORD': None,
                'OS_TENANT_NAME': None,
                'OS_AUTH_URL': None}

OPENRC = '/root/openrc'
TOKEN_FILE = '/root/.token'


def get_token_from_file(auth_details):
    if os.path.exists('/root/.token'):
        token_file = open(TOKEN_FILE)
        os_auth_token = token_file.readline()
        token_file.close()

        return os_auth_token
    else:
        return keystone_auth(auth_details)


def keystone_auth(auth_details):
    try:
        keystone = client.Client(username=auth_details['OS_USERNAME'],
                                 password=auth_details['OS_PASSWORD'],
                                 tenant_name=auth_details['OS_TENANT_NAME'],
                                 auth_url=auth_details['OS_AUTH_URL'])
    except (exceptions.Unauthorized, exceptions.AuthorizationFailure) as e:
        print "status err %s" % e
        sys.exit(1)

    token_file = open(TOKEN_FILE, 'w')
    token_file.write("%s\n" % keystone.auth_ref['token']['id'])
    token_file.close()

    return keystone.auth_ref['token']['id']


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
