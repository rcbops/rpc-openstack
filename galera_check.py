#!/usr/bin/env python
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

RETCODE, OUTPUT, ERR = galera_status_check('/usr/bin/mysql \
       --defaults-file=/root/.my.cnf \
       -e "SHOW STATUS WHERE Variable_name REGEXP \'^(wsrep.*|queries)\'"')

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

    if (SLAVE_STATUS['wrsep_local_state_uuid'] !=
            SLAVE_STATUS['wsrep_cluster_state_uuid']):
        status_err("the local node is out of sync")

    if (int(SLAVE_STATUS['wsrep_local_state']) == 4 and
            SLAVE_STATUS['wsrep_local_state_comment'] == "Synced"):

        status_ok()
        metric('WSREP_REPLICATED_BYTES', 'int',
               SLAVE_STATUS['wsrep_replicated_bytes'])
        metric('WSREP_RECEIVED_BYTES', 'int',
               SLAVE_STATUS['wsrep_received_bytes'])
        metric('WSREP_COMMIT_WINDOW', 'float',
               SLAVE_STATUS['wsrep_commit_window'])
        metric('WSREP_CLUSTER_SIZE', 'int', SLAVE_STATUS['wsrep_cluster_size'])
        metric('QUERIES_PER_SECOND', 'int', SLAVE_STATUS['Queries'])
        metric('WSREP_CLUSTER_STATE_UUID', 'string',
               SLAVE_STATUS['wsrep_cluster_state_uuid'])
        metric('WSREP_CLUSTER_STATUS', 'string',
               SLAVE_STATUS['wsrep_cluster_status'])
        metric('WSREP_LOCAL_STATE_UUID', 'string',
               SLAVE_STATUS['wsrep_local_state_uuid'])
        metric('WSREP_LOCAL_STATE_COMMENT', 'string',
               SLAVE_STATUS['wsrep_local_state_comment'])
