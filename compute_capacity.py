#!/usr/bin/env python

from nova import config
from nova import context
from nova.db import api
from nova.scheduler import host_manager
from nova.scheduler.filters import ram_filter

from maas_common import status_ok, metric


def main():
    config.parse_args([])
    ctxt = context.get_admin_context()
    compute_hosts = api.compute_node_get_all(ctxt)

    total_ram_mb_free = 0
    total_disk_mb_free = 0

    for compute_host in compute_hosts:
        if 'RamFilter' in host_manager.CONF.scheduler_default_filters:
            total_ram_mb_free += (compute_host['free_ram_mb'] *
                                  ram_filter.CONF.ram_allocation_ratio)
        else:
            total_ram_mb_free += compute_host['free_ram_mb']

        total_disk_mb_free += compute_host['free_disk_gb'] * 1024

    status_ok()
    metric('total_ram_mb_free', 'int64', total_ram_mb_free)
    metric('total_disk_mb_free', 'int64', total_disk_mb_free)


if __name__ == "__main__":
    main()
