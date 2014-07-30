#!/usr/bin/env python

import requests
from requests import exceptions as exc
from maas_common import (get_auth_ref, get_heat_client, get_keystone_client,
                         metric, status_ok, status_err)


def check_heat(tenant, token):
    endpoint = 'http://127.0.0.1:8004/v1/{0}'.format(tenant)
    get_heat_client(endpoint, token)

    status_ok()
    metric('heat_api_local_status', 'uint32', 1)


def main():
    keystone = get_keystone_client(get_auth_ref())
    tenant = keystone.tenant_id
    token = keystone.auth_ref['token']['id']

    check_heat(tenant, token)

if __name__ == "__main__":
    main()
