#!/usr/bin/env python

# idea borrowed from nova/cells/state.py
# note that this does not take into account ram_allocation_ratio which by
# default allows memory overcommitting

from nova import config
from nova import context
from nova.db import api

config.parse_args([])
ctxt = context.get_admin_context()
compute_hosts = api.compute_node_get_all(ctxt)

total_ram_mb_free = 0
total_disk_mb_free = 0

for compute_host in compute_hosts:
    total_ram_mb_free += compute_host['free_ram_mb']
    total_disk_mb_free += compute_host['free_disk_gb'] * 1024

print "status success"
print "metric total_ram_mb_free int64 %d" % total_ram_mb_free
print "metric total_disk_mb_free int64 %d" % total_disk_mb_free
