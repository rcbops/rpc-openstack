#!/usr/bin/env python

import datetime
import json
import os
import re
import sys

AUTH_DETAILS = {'OS_USERNAME': None,
                'OS_PASSWORD': None,
                'OS_TENANT_NAME': None,
                'OS_AUTH_URL': None}

OPENRC = '/root/openrc'
TOKEN_FILE = '/root/.auth_ref.json'


try:
    from glanceclient import Client as g_client
    from glanceclient import exc as g_exc
except ImportError:
    def get_glance_client(*args, **kwargs):
        status_err('Cannot import glanceclient')
else:
    def get_glance_client(token, endpoint, previous_tries=0):
        if previous_tries > 3:
            return None

        glance = g_client('1', endpoint=endpoint, token=token)

        try:
            # We don't want to be pulling massive lists of images every time we
            # run
            image = glance.images.list(limit=1)
            # Exceptions are only thrown when we iterate over image
            [i.id for i in image]
        except g_exc.HTTPUnauthorized as e:
            get_glance_client(token, endpoint, previous_tries + 1)
        except Exception as e:
            status_err(str(e))

        return glance

try:
    from keystoneclient.v2_0 import client as k_client
    from keystoneclient.openstack.common.apiclient import exceptions as k_exc
except ImportError:
    def keystone_auth(*args, **kwargs):
        status_err('Cannot import keystoneclient')

    def get_keystone_client(*args, **kwargs):
        status_err('Cannot import keystoneclient')
else:
    def keystone_auth(auth_details):
        try:
            tenant_name = auth_details['OS_TENANT_NAME']
            keystone = k_client.Client(username=auth_details['OS_USERNAME'],
                                       password=auth_details['OS_PASSWORD'],
                                       tenant_name=tenant_name,
                                       auth_url=auth_details['OS_AUTH_URL'])
        except Exception as e:
            status_err(str(e))

        try:
            with open(TOKEN_FILE, 'w') as token_file:
                json.dump(keystone.auth_ref, token_file)
        except IOError:
            # if we can't write the file we go on
            pass

        return keystone.auth_ref

    def get_keystone_client(auth_ref, previous_tries=0, endpoint=None):
        if previous_tries > 3:
            return None

        if endpoint is None:
            keystone = k_client.Client(auth_ref=auth_ref)
        else:
            keystone = k_client.Client(auth_ref=auth_ref, endpoint=endpoint)

        try:
            # This should be a rather light-weight call that validates we're
            # actually connected/authenticated.
            keystone.services.list()
        except (k_exc.AuthorizationFailure, k_exc.Unauthorized):
            # Force an update of auth_ref
            auth_details = get_auth_details()
            auth_ref = keystone_auth(auth_details)
            keystone = get_keystone_client(auth_ref,
                                           previous_tries + 1,
                                           endpoint)
        except Exception as e:
            status_err(str(e))

        return keystone


try:
    from neutronclient.neutron import client as n_client
    from neutronclient.common import exceptions as n_exc
except ImportError:
    def get_neutron_client(*args, **kwargs):
        status_err('Cannot import neutronclient')
else:
    def get_neutron_client(token, endpoint_url, previous_tries=0):
        if previous_tries > 3:
            return None

        neutron = n_client.Client('2.0',
                                  token=token,
                                  endpoint_url=endpoint_url)

        try:
            # some arbitrary command that should always have at least 1 result
            agents = neutron.list_agents()
            # iterate the list to ensure we actually have something
            [i['id'] for i in agents['agents']]
        except (n_exc.Unauthorized,
                n_exc.ConnectionFailed,
                n_exc.Forbidden) as e:
            get_neutron_client(token, endpoint_url, previous_tries + 1)
        except n_exc.NeutronException as e:
            status_err(str(e))

        return neutron


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


def get_auth_details(openrc_file=OPENRC):
    auth_details = AUTH_DETAILS
    pattern = re.compile(
        '^(?:export\s)?(?P<key>\w+)(?:\s+)?=(?:\s+)?(?P<value>.*)$'
    )

    if os.path.exists(openrc_file):
        with open(openrc_file) as openrc:
            for line in openrc:
                match = pattern.match(line)
                if match is None:
                    continue
                k = match.group('key')
                v = match.group('value')
                if k in auth_details and auth_details[k] is None:
                    auth_details[k] = v
    else:
        # no openrc file, so we try the environment
        for key in auth_details.keys():
            auth_details[key] = os.environ.get(key)

    for key in auth_details.keys():
        if auth_details[key] is None:
            status_err('%s not set' % key)

    return auth_details


def status(status, message):
    status_line = 'status %s' % status
    if message is not None:
        status_line = ' '.join((status_line, message))
    print status_line


def status_err(message=None):
    status('err', message)
    sys.exit(1)


def status_ok(message=None):
    status('ok', message)


def metric(name, metric_type, value, unit=None):
    metric_line = 'metric %s %s %s' % (name, metric_type, value)
    if unit is not None:
        metric_line = ' '.join((metric_line, unit))
    print metric_line
