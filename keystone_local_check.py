#!/usr/bin/env python

from maas_common import get_auth_ref, get_keystone_client
from maas_common import status_err, status_ok, metric
import re
import sys

ENDPOINT = 'http://127.0.0.1:35357/v2.0'


def check(auth_ref):
    keystone = get_keystone_client(auth_ref, endpoint=ENDPOINT)

    if keystone is None:
        status_err('Unable to obtain valid keystone client, cannot proceed')

    users = keystone.users.list()

    status_ok()
    metric('keystone_local_status', 'uint32', 1)


def main():
    auth_ref = get_auth_ref()
    check(auth_ref)

if __name__ == "__main__":
    main()
