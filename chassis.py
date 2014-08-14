import re
import sys
import subprocess

from maas_common import status_err, status_ok, metric_bool

OKAY = re.compile('(?:Health|Status)\s+:\s+(\w+)')


def chassis_report(report_type):
    """Return the report as a string."""
    return subprocess.check_output(['omreport', 'chassis', report_type])


def all_okay(report):
    """Determine if the installed health and status fields are okay.

    :returns: True if all "Ok", False otherwise
    :rtype: bool
    """
    return all(v.lower() == 'ok' for v in OKAY.findall(report))


def main():
    if len(sys.argv[1:]) != 1:
        status_err(
            'Too many arguments provided: "%s"' % ' '.join(sys.argv[1:])
        )

    report_type = sys.argv[1].lower()

    try:
        report = chassis_report(report_type)
    except OSError as e:
        status_err(str(e))

    status_ok()
    metric_bool('%s_okay' % report_type, all_okay(report))


if __name__ == '__main__':
    main()
