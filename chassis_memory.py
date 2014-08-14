import re
import subprocess

from maas_common import status_err, status_ok, metric_bool

OKAY = re.compile('(?:Health|Status)\s+:\s+(\w+)')


def chassis_memory_report():
    """Return the report as a string."""
    return subprocess.check_output(['omreport', 'chassis', 'memory'])


def memory_okay(report):
    """Determine if the installed memory array is okay.

    :returns: True if all "Ok", False otherwise
    :rtype: bool
    """
    return all(v.lower() == 'ok' for v in OKAY.findall(report))


def main():
    try:
        report = chassis_memory_report()
    except OSError as e:
        status_err(str(e))

    status_ok()
    metric_bool('memory_okay', memory_okay(report))


if __name__ == '__main__':
    main()
