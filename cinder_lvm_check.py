#!/usr/bin/env python
import os
import sys
import subprocess


def execute(cmd):
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return process.communicate()


def get_volume_group_info(vg_name):
    """Get volume group stats. Note that this must run as root."""
    out, err = execute(['env', 'LC_ALL=C', 'vgs', '--noheadings',
                        '--nosuffix', '--units', 'g', '-o',
                        'size,free,lv_count', '--separator', ':',
                        vg_name])

    vg_info = None
    if out is not None:
        fields = out.split()[0].split(':')
        vg_info = {'size': float(fields[0]),
                   'free': float(fields[1]),
                   'count': int(fields[2])}

    return vg_info


def set_auth_details():
    auth_details = {'OS_USERNAME': None,
                    'OS_PASSWORD': None,
                    'OS_TENANT_NAME': None,
                    'OS_AUTH_URL': None}

    for key in auth_details.keys():
        if key in os.environ:
            auth_details[key] = os.environ[key]

    return auth_details


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
