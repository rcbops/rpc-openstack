#!/usr/bin/env python

import datetime
import json
import os
import re
import sys

from keystoneclient.v2_0 import client
from keystoneclient.openstack.common.apiclient import exceptions

AUTH_DETAILS = {'OS_USERNAME': None,
                'OS_PASSWORD': None,
                'OS_TENANT_NAME': None,
                'OS_AUTH_URL': None}

OPENRC = '/root/openrc'
TOKEN_FILE = '/root/.auth_ref.json'


def is_token_expired(token):
    expires = datetime.datetime.strptime(token['expires'],
                                         '%Y-%m-%dT%H:%M:%SZ')
    return datetime.datetime.now() >= expires


def get_auth_ref():
    auth_details = get_auth_details()
    auth_ref = get_auth_from_file()
    if auth_ref is None:
        auth_ref = keystone_auth(auth_details)

    if is_token_expired(auth_ref['token']):
        auth_ref = keystone_auth(auth_details)

    return auth_ref


def get_auth_from_file():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as token_file:
            auth_ref = json.load(token_file)

        return auth_ref
    return None


def keystone_auth(auth_details):
    try:
        keystone = client.Client(username=auth_details['OS_USERNAME'],
                                 password=auth_details['OS_PASSWORD'],
                                 tenant_name=auth_details['OS_TENANT_NAME'],
                                 auth_url=auth_details['OS_AUTH_URL'])
    except (exceptions.Unauthorized, exceptions.AuthorizationFailure) as e:
        print "status err %s" % e
        sys.exit(1)

    with open(TOKEN_FILE, 'w') as token_file:
        json.dump(keystone.auth_ref, token_file)

    return keystone.auth_ref


def get_auth_details():
    auth_details = AUTH_DETAILS
    pattern = re.compile(
        '^(?:export\s)?(?P<key>\w+)(?:\s+)?=(?:\s+)?(?P<value>.*)$'
    )

    with open(OPENRC) as openrc:
        for line in openrc:
            match = pattern.match(line)
            if match is None:
                continue
            k = match.group('key')
            v = match.group('value')
            if k in auth_details and auth_details[k] is None:
                auth_details[k] = v

    for key in auth_details.keys():
        if auth_details[key] is None:
            print "status err %s not set" % key
            sys.exit(1)

    return auth_details
