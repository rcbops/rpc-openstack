#!/usr/bin/env python
import sys
import subprocess


def get_volume_group_info(vg_name):
    """Get volume group stats. Note that this must run as root."""
    try:
        out = subprocess.check_output(['env', 'LC_ALL=C', 'vgs', '--noheadings',
                                       '--nosuffix', '--units', 'g', '-o',
                                       'size,free,lv_count', '--separator', ':',
                                       vg_name],
                                       stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        return None

    vg_info = None
    if out is not None:
        fields = out.split(':')
        if len(fields) == 3:
            vg_info = {'size': float(fields[0]),
                       'free': float(fields[1]),
                       'count': int(fields[2])}

    return vg_info


def main():
    if len(sys.argv) < 2:
        print 'status err volume group name must be given as an argument'
        sys.exit(1)

    vg_name = sys.argv[1]
    vg_stats = get_volume_group_info(vg_name)
    if vg_stats is None:
        print 'status err volume group info could not be obtained'
        sys.exit(1)

    print 'status OK'
    print 'metric volume_group_size uint32 %d' % vg_stats['size']
    print 'metric volume_group_free uint32 %d' % vg_stats['free']
    print 'metric volume_group_count uint32 %d' % vg_stats['count']

if __name__ == "__main__":
    main()
