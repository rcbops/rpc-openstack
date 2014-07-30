#!/usr/bin/env python

from maas_common import (get_auth_ref, get_nova_client, status_err,
                         status_ok, metric)

COMPUTE_ENDPOINT = 'http://127.0.0.1:8774/v3'


def check(token):
    nova = get_nova_client(token, COMPUTE_ENDPOINT)
    if nova is None:
        status_err('Unable to obtain valid nova client, cannot proceed')

    status_ok()
    metric('nova_api_local_status', 'uint32', 1)


def main():
    auth_ref = get_auth_ref()
    token = auth_ref['token']['id']
    check(token)


if __name__ == "__main__":
    main()
