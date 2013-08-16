#!/usr/bin/env python

import os
import subprocess
import sys


def main():
    if len(sys.argv) != 3:
        error()

    parser = sys.argv[1]
    log_file = sys.argv[2]

    if not os.path.exists(log_file):
        error()

    cmd = "logster -o stdout %s %s" % (parser, log_file)

    p = subprocess.Popen(cmd.split(),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    result = p.communicate()[0].splitlines()

    if len(result) < 5:
        error()

    print "status ok"

    for r in result:
        s = r.split()
        print "metric %s double %s" % (s[1], s[2])


def error():
    print "status error"
    sys.exit(1)


if __name__ == "__main__":
    main()
