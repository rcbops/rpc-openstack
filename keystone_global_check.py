#!/usr/bin/env python

from maas_common import (get_keystone_client, status_err, status_ok, metric,
                         metric_bool)
from keystoneclient.openstack.common.apiclient import exceptions as k_exc


def check():
    try:
        keystone = get_keystone_client()

        users = keystone.users.list()
        enabled = [u for u in users if u.enabled is True]

        status_ok()
        metric_bool('keystone_global_status', True)
        metric('keystone_users', 'uint32', len(enabled))
    except k_exc.ClientException:
        status_ok()
        metric_bool('keystone_global_status', False)
    except Exception as e:
        status_err(str(e))


def main():
    check()

if __name__ == "__main__":
    main()
