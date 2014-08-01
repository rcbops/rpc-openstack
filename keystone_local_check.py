#!/usr/bin/env python

from maas_common import (get_keystone_client, status_err, status_ok, metric,
                         metric_bool)
from keystoneclient.openstack.common.apiclient import exceptions as k_exc

ENDPOINT = 'http://127.0.0.1:35357/v2.0'


def check():
    try:
        keystone = get_keystone_client(endpoint=ENDPOINT)

        keystone.users.list()

        status_ok()
        metric_bool('keystone_local_status', True)
    except k_exc.ClientException:
        status_ok()
        metric_bool('keystone_local_status', False)
    except Exception as e:
        status_err(str(e))


def main():
    check()

if __name__ == "__main__":
    main()
