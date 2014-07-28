#!/usr/bin/env python

import sys
import psutil
import os

try:
    procname = sys.argv[1]
except IndexError:
    print 'script takes a single argument - the process name to check for'
    sys.exit(1)

matching_procs = [p.pid for p in psutil.get_process_list() if
                  (procname in str(p.cmdline) and
                  p.pid != os.getpid())]

if not matching_procs:
    print 'status err: no process running that matches %s' % procname
    sys.exit(1)

print 'status OK'
print 'metric num_running_processes uint32 %d' % len(matching_procs)
