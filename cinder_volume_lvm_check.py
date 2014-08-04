#!/usr/bin/env python
import sys
import subprocess

from maas_common import status_err, status_ok, metric


def get_volume_group_info(vg_name):
    """Get volume group stats. Note that this must run as root."""
    cmd = ['env', 'LC_ALL=C', 'vgs', '--noheadings', '--nosuffix', '--units',
           'g', '-o', 'size,free,lv_count', '--separator', ':', vg_name]
    try:
        out = subprocess.check_output(cmd,
                                      stderr=subprocess.STDOUT,
                                      close_fds=True)
    except subprocess.CalledProcessError:
        return None

    vg_info = None
    if out is not None:
        fields = out.split(':')
        if len(fields) == 3:
            vg_info = {'size': float(fields[0]),
                       'free': float(fields[1]),
                       'count': int(fields[2])}
        else:
            status_err(out)

    return vg_info


def main():
    if len(sys.argv) < 2:
        status_err('volume group name must be given as an argument')

    vg_name = sys.argv[1]
    vg_stats = get_volume_group_info(vg_name)
    if vg_stats is None:
        status_err('volume group info could not be obtained')

    status_ok()
    metric('volume_group_size', 'uint32', vg_stats['size'])
    metric('volume_group_free', 'uint32', vg_stats['free'])
    metric('volume_group_count', 'uint32', vg_stats['count'])

if __name__ == "__main__":
    main()
