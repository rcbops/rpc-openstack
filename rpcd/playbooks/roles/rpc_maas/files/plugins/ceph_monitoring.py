#!/usr/bin/env python

# Copyright 2015, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json
import maas_common
import subprocess


STATUSES = {'HEALTH_OK': 2, 'HEALTH_WARN': 1, 'HEALTH_ERR': 0}


def check_command(command):
    output = subprocess.check_output(command, stderr=subprocess.STDOUT)
    lines = output.strip().split('\n')
    return json.loads(lines[-1])


def get_ceph_status(client, keyring, fmt='json'):
    return check_command(('ceph', '--format', fmt, '--name', client,
                          '--keyring', keyring, 'status'))


def get_ceph_pg_dump_osds(client, keyring, fmt='json'):
    return check_command(('ceph', '--format', fmt, '--name', client,
                          '--keyring', keyring, 'pg', 'dump', 'osds'))


def get_ceph_osd_dump(client, keyring, fmt='json'):
    return check_command(('ceph', '--format', fmt, '--name', client,
                          '--keyring', keyring, 'osd', 'dump'))


def get_mon_statistics(client=None, keyring=None, host=None):
    ceph_status = get_ceph_status(client=client, keyring=keyring)
    mon = [m for m in ceph_status['monmap']['mons']
           if m['name'] == host]
    mon_in = mon[0]['rank'] in ceph_status['quorum']
    maas_common.metric_bool('mon_in_quorum', mon_in)
    health_status = 0
    for each in ceph_status['health']['health']['health_services'][0]['mons']:
        if each['name'] == host:
            health_status = STATUSES[each['health']]
            break
    maas_common.metric('mon_health', 'uint32', health_status)


def get_osd_statistics(client=None, keyring=None, osd_ids=None):
    osd_dump = get_ceph_osd_dump(client=client, keyring=keyring)
    pg_osds_dump = get_ceph_pg_dump_osds(client=client, keyring=keyring)
    for osd_id in osd_ids:
        osd_ref = 'osd.%s' % osd_id
        for _osd in osd_dump['osds']:
            if _osd['osd'] == osd_id:
                osd = _osd
                break
        else:
            msg = 'The OSD ID %s does not exist.' % osd_id
            raise maas_common.MaaSException(msg)

        key = 'up'
        name = '_'.join((osd_ref, key))
        maas_common.metric_bool(name, osd[key])

        for _osd in pg_osds_dump:
            if _osd['osd'] == osd_id:
                osd = _osd
                break


def get_cluster_statistics(client=None, keyring=None):
    metrics = []

    ceph_status = get_ceph_status(client=client, keyring=keyring)
    # Get overall cluster health
    metrics.append({
        'name': 'cluster_health',
        'type': 'uint32',
        'value': STATUSES[ceph_status['health']['overall_status']]})

    # Collect epochs for the mon and osd maps
    metrics.append({'name': "monmap_epoch",
                    'type': 'uint32',
                    'value': ceph_status['monmap']['epoch']})
    metrics.append({'name': "osdmap_epoch",
                    'type': 'uint32',
                    'value': ceph_status['osdmap']['osdmap']['epoch']})

    # Collect OSDs per state
    osds = {'total': ceph_status['osdmap']['osdmap']['num_osds'],
            'up': ceph_status['osdmap']['osdmap']['num_up_osds'],
            'in': ceph_status['osdmap']['osdmap']['num_in_osds']}
    for k in osds:
        metrics.append({'name': 'osds_%s' % k,
                        'type': 'uint32',
                        'value': osds[k]})

    # Collect cluster size & utilisation
    metrics.append({'name': 'osds_kb_used',
                    'type': 'uint64',
                    'value': ceph_status['pgmap']['bytes_used'] / 1024})
    metrics.append({'name': 'osds_kb_avail',
                    'type': 'uint64',
                    'value': ceph_status['pgmap']['bytes_avail'] / 1024})
    metrics.append({'name': 'osds_kb',
                    'type': 'uint64',
                    'value': ceph_status['pgmap']['bytes_total'] / 1024})

    # Collect num PGs and num healthy PGs
    pgs = {'total': ceph_status['pgmap']['num_pgs'], 'active_clean': 0}
    for state in ceph_status['pgmap']['pgs_by_state']:
        if state['state_name'] == 'active+clean':
            pgs['active_clean'] = state['count']
            break
    for k in pgs:
        metrics.append({'name': 'pgs_%s' % k,
                        'type': 'uint32',
                        'value': pgs[k]})

    # Submit gathered metrics
    for m in metrics:
        maas_common.metric(m['name'], m['type'], m['value'])


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True, help='Ceph client name')
    parser.add_argument('--keyring', required=True, help='Ceph client keyring')

    subparsers = parser.add_subparsers(dest='subparser_name')

    parser_mon = subparsers.add_parser('mon')
    parser_mon.add_argument('--host', required=True, help='Mon hostname')

    parser_osd = subparsers.add_parser('osd')
    parser_osd.add_argument('--osd_ids', required=True,
                            help='Space separated list of OSD IDs')

    subparsers.add_parser('cluster')
    return parser.parse_args()


def main(args):
    get_statistics = {'cluster': get_cluster_statistics,
                      'mon': get_mon_statistics,
                      'osd': get_osd_statistics}
    kwargs = {'client': args.name, 'keyring': args.keyring}
    if args.subparser_name == 'osd':
        kwargs['osd_ids'] = [int(i) for i in args.osd_ids.split(' ')]
    if args.subparser_name == 'mon':
        kwargs['host'] = args.host
    get_statistics[args.subparser_name](**kwargs)
    maas_common.status_ok()


if __name__ == '__main__':
    with maas_common.print_output():
        args = get_args()
        main(args)
