#!/usr/bin/env python

import collections
import os
import psutil
import sys

from maas_common import metric, status_err, status_ok


procnames = sys.argv[1:]
if not procnames:
    status_err('script takes between 1 and 10 arguments, each being'
               ' a process name to check for')
# single monitor can only report up to 10 metrics
if len(procnames) > 10:
    status_err('script takes at most 10 process names to check for')

results = collections.Counter(**{proc: 0 for proc in procnames})
for to_match in procnames:
    for proc in psutil.process_iter():
        if not proc.cmdline():
            continue
        if to_match in proc.cmdline()[0] and proc.pid != os.getpid():
            results.update((to_match, ))

status_ok()
for proc, count in results.viewitems():
    metric('num_running_processes_%s' % proc, 'uint32', count)
