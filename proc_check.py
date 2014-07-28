#!/usr/bin/env python

import collections
import os
import psutil
import sys


def err(reason):
    print 'status err', reason
    sys.exit(1)

procnames = sys.argv[1:]
if not procnames:
    err('script takes a single argument - the process name to check for')
    sys.exit(1)
# single monitor can only report up to 10 metrics
if len(procnames) > 10:
    err('script takes at most 10 process names to check for')

results = collections.Counter(**{proc: 0 for proc in procnames})
for to_match in procnames:
    for proc in psutil.process_iter():
        if (to_match in str(proc.cmdline) and proc.pid != os.getpid()):
            results.update((to_match, ))

print 'status OK'
for proc, count in results.viewitems():
    print 'metric num_running_processes_%s uint32 %d' % (proc, count)
