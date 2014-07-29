#!/usr/bin/env python

from maas_common import get_auth_ref, get_glance_client
from maas_common import status_err, status_ok, metric
import sys

IMAGE_ENDPOINT = 'http://127.0.0.1:9292'


def check(token):
    glance = get_glance_client(token, IMAGE_ENDPOINT)
    if glance is None:
        status_err('Unable to obtain valid glance client, cannot proceed')

    status_ok()
    metric('glance_api_local_status', 'uint32', 1)


def main():
    auth_ref = get_auth_ref()
    token = auth_ref['token']['id']
    check(token)


if __name__ == "__main__":
    main()
