#!/usr/bin/env python

import re
import sys
import subprocess

from maas_common import status_err, status_ok, metric_bool

CHASSIS = re.compile('(?:Health)\s+:\s+(\w+)')
STORAGE = re.compile('(?:Status)\s+:\s+(\w+)')
regex = {'storage': STORAGE, 'chassis': CHASSIS}

def hardware_report(report_type, report_request):
    """Return the report as a string."""
    return subprocess.check_output(['/opt/dell/srvadmin/bin/omreport', report_type, report_request])


def all_okay(report, regex_find):
    """Determine if the installed health and status fields are okay.

    :returns: True if all "Ok", False otherwise
    :rtype: bool
    """
    return all(v.lower() == 'ok' for v in regex_find.findall(report))


def main():
    if len(sys.argv[1:]) != 2:
        status_err(
            'Requires 2 arguments, arguments provided: "%s"' % ' '.join(sys.argv[1:])
        )

    report_type = sys.argv[1].lower()
    report_request = sys.argv[2].lower()

    try:
        report = hardware_report(report_type, report_request)
    except (OSError, subprocess.CalledProcessError) as e:
        status_err(str(e))

    status_ok()
    metric_bool('hardware_%s_status' % report_request, all_okay(report, regex[report_type]))


if __name__ == '__main__':
    main()
