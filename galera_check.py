#!/usr/bin/env python

# Copyright 2014, Rackspace US, Inc.
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

import optparse
import subprocess
import shlex

from maas_common import status_err, status_ok, metric


def galera_status_check(arg):
    proc = subprocess.Popen(shlex.split(arg),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=False)

    out, err = proc.communicate()
    ret = proc.returncode
    return ret, out, err


def generate_query(host, port):
    if host:
        host = ' -h %s' % host
    else:
        host = ''

    if port:
        port = ' -P %s' % port
    else:
        port = ''

    return ('/usr/bin/mysql --defaults-file=/root/.my.cnf'
            '%s%s -e "SHOW STATUS WHERE Variable_name REGEXP '
            "'^(wsrep.*|queries)'\"") % (host, port)


def parse_args():
    parser = optparse.OptionParser(usage='%prog [-h] [-H hostname] [-P port]')
    parser.add_option('-H', '--host', action='store', dest='host',
                      default=None,
                      help='Host to override the defaults with')
    parser.add_option('-P', '--port', action='store', dest='port',
                      default=None,
                      help='Port to override the defauults with')
    return parser.parse_args()


def print_metrics(replica_status):
    status_ok()
    metric('WSREP_REPLICATED_BYTES', 'int64',
           replica_status['wsrep_replicated_bytes'])
    metric('WSREP_RECEIVED_BYTES', 'int64',
           replica_status['wsrep_received_bytes'])
    metric('WSREP_COMMIT_WINDOW', 'double',
           replica_status['wsrep_commit_window'])
    metric('WSREP_CLUSTER_SIZE', 'int64',
           replica_status['wsrep_cluster_size'])
    metric('QUERIES_PER_SECOND', 'int64',
           replica_status['Queries'])
    metric('WSREP_CLUSTER_STATE_UUID', 'string',
           replica_status['wsrep_cluster_state_uuid'])
    metric('WSREP_CLUSTER_STATUS', 'string',
           replica_status['wsrep_cluster_status'])
    metric('WSREP_LOCAL_STATE_UUID', 'string',
           replica_status['wsrep_local_state_uuid'])
    metric('WSREP_LOCAL_STATE_COMMENT', 'string',
           replica_status['wsrep_local_state_comment'])


def main():
    options, _ = parse_args()

    retcode, output, err = galera_status_check(
        generate_query(options.host, options.port)
    )

    if retcode > 0:
        status_err(err)

    if not output:
        status_err('No output received from mysql. Cannot gather metrics.')

    show_status_list = output.split('\n')[1:-1]
    replica_status = {}
    for i in show_status_list:
        replica_status[i.split('\t')[0]] = i.split('\t')[1]

    if replica_status['wsrep_cluster_status'] != "Primary":
        status_err("there is a partition in the cluster")

    if (replica_status['wsrep_local_state_uuid'] !=
            replica_status['wsrep_cluster_state_uuid']):
        status_err("the local node is out of sync")

    if (int(replica_status['wsrep_local_state']) == 4 and
            replica_status['wsrep_local_state_comment'] == "Synced"):
        print_metrics(replica_status)


if __name__ == '__main__':
    main()
