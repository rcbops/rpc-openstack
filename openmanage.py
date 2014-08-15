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
    fields = regex_find.findall(report)
    if not fields:
        status_err('There were no Health or Status fields to check.')
    return all(v.lower() == 'ok' for v in fields)


def main():
    if len(sys.argv[1:]) != 2:
        args = ' '.join(sys.argv[1:])
        status_err(
<<<<<<< HEAD
            'Requires 2 arguments, arguments provided: "%s"'
            % ' '.join(sys.argv[1:])
=======
            'Requires 2 arguments, arguments provided: "%s"' % args
>>>>>>> Shorten the line length
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
