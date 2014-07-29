#!/usr/bin/env python

from maas_common import (get_neutron_client, get_auth_ref,
                         status_err, status_ok, metric)

NETWORK_ENDPOINT = 'http://127.0.0.1:9696'


def check(token):

    neutron = get_neutron_client(token, NETWORK_ENDPOINT)

    if neutron is None:
        status_err("Unable to obtain valid neutron client, cannot proceed")

    status_ok()
    metric('neutron_api_local_status', 'uint32', 1)


def main():
    auth_ref = get_auth_ref()
    token = auth_ref['token']['id']
    check(token)


if __name__ == "__main__":
    main()
