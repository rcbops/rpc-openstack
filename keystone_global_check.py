#!/usr/bin/env python

from maas_common import get_auth_ref, get_keystone_client
from maas_common import status_err, status_ok, metric
import sys


def check(auth_ref):
    keystone = get_keystone_client(auth_ref)

    if keystone is None:
        status_err('Unable to obtain valid keystone client, cannot proceed')

    users = keystone.users.list()
    enabled = [u for u in users if u.enabled is True]

    status_ok()
    metric('keystone_users', 'uint32', len(enabled))


def main():
    auth_ref = get_auth_ref()
    check(auth_ref)

if __name__ == "__main__":
    main()
