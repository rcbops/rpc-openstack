#!/usr/bin/env python

from maas_common import get_auth_ref, status_err, status_ok, metric
import os
import re
import subprocess
import sys

CACHE_DIR = '/var/lib/glance/cache'
METRIC_PREFIX = 'glance_api_local_cache'
UUID_FORMAT = re.compile('[0-9a-z]{8}-([0-9a-z]{4}-){3}[0-9a-z]{12}')


def is_uuid(str):
    if UUID_FORMAT.match(str):
        return True
    return False


def main():
    auth_ref = get_auth_ref()
    token = auth_ref['token']['id']
    user = auth_ref['user']['username']
    tenant = auth_ref['token']['tenant']['name']

    if not os.path.exists(CACHE_DIR):
        status_err("Directory %s does not exist" % CACHE_DIR)

    try:
        output = subprocess.check_output(['glance-cache-manage',
                                          '--host=localhost',
                                          "--os-username=%s" % user,
                                          "--os-tenant-name=%s" % tenant,
                                          "--os-auth-token=%s" % token,
                                          'list-cached'])
    except subprocess.CalledProcessError:
        # We don't capture and print the exception as it will contain our
        # API token, which shouldn't get sent to MaaS
        status_err("glance-cache-manage returned a non-zero exit status")

    expected_cached = []
    actual_cached = []

    for lines in output.splitlines():
        entry = lines.split()
        if is_uuid(entry[0]):
            expected_cached.append(entry[0])

    for i in os.listdir(CACHE_DIR):
        if is_uuid(i) and os.path.isfile(i):
            actual_cached.append(i)

    status_ok()
    metric("%s_expected" % METRIC_PREFIX, 'uint32', len(expected_cached))
    metric("%s_actual" % METRIC_PREFIX, 'uint32', len(actual_cached))


if __name__ == "__main__":
    main()
