#!/usr/bin/env python
import optparse
import sys
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

parser = optparse.OptionParser(usage='%prog [-h] [-H hostname] [-P port]')
parser.add_option('-H', '--host', action='store', dest='host', default=None,
                  help='Host to override the defaults with')
parser.add_option('-P', '--port', action='store', dest='port', default=None,
                  help='Port to override the defauults with')
options, _ = parser.parse_args()

RETCODE, OUTPUT, ERR = galera_status_check(generate_query(options.host,
                                                          options.port))

if RETCODE:
    print >> sys.stderr, "There was an error (%d):\n" % RETCODE
    print >> sys.stderr, ERR

if OUTPUT != "":
    SHOW_STATUS_LIST = OUTPUT.split('\n')
    del SHOW_STATUS_LIST[0]
    del SHOW_STATUS_LIST[-1]

    SLAVE_STATUS = {}
    for i in SHOW_STATUS_LIST:
        SLAVE_STATUS[i.split('\t')[0]] = i.split('\t')[1]

    if SLAVE_STATUS['wsrep_cluster_status'] != "Primary":
        status_err("there is a partition in the cluster")

    if (SLAVE_STATUS['wsrep_local_state_uuid'] !=
            SLAVE_STATUS['wsrep_cluster_state_uuid']):
        status_err("the local node is out of sync")

    if (int(SLAVE_STATUS['wsrep_local_state']) == 4 and
            SLAVE_STATUS['wsrep_local_state_comment'] == "Synced"):

        status_ok()
        metric('WSREP_REPLICATED_BYTES', 'int64',
               SLAVE_STATUS['wsrep_replicated_bytes'])
        metric('WSREP_RECEIVED_BYTES', 'int64',
               SLAVE_STATUS['wsrep_received_bytes'])
        metric('WSREP_COMMIT_WINDOW', 'double',
               SLAVE_STATUS['wsrep_commit_window'])
        metric('WSREP_CLUSTER_SIZE', 'int64',
               SLAVE_STATUS['wsrep_cluster_size'])
        metric('QUERIES_PER_SECOND', 'int64',
               SLAVE_STATUS['Queries'])
        metric('WSREP_CLUSTER_STATE_UUID', 'string',
               SLAVE_STATUS['wsrep_cluster_state_uuid'])
        metric('WSREP_CLUSTER_STATUS', 'string',
               SLAVE_STATUS['wsrep_cluster_status'])
        metric('WSREP_LOCAL_STATE_UUID', 'string',
               SLAVE_STATUS['wsrep_local_state_uuid'])
        metric('WSREP_LOCAL_STATE_COMMENT', 'string',
               SLAVE_STATUS['wsrep_local_state_comment'])
