#!/usr/bin/env python
import sys
import subprocess
import shlex

def galera_status_check(arg):
    proc = subprocess.Popen(shlex.split(arg),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=False)

    out,err = proc.communicate()
    ret = proc.returncode
    return ret, out, err

RETCODE, OUTPUT, ERR = galera_status_check('/usr/bin/mysql \
       --defaults-file=/root/.my.cnf \
       -e "SHOW STATUS LIKE \'wsrep%\'"')

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
        print "status err there is a partition in the cluster."

    if int(SLAVE_STATUS['wsrep_local_state']) == 4 and \
            SLAVE_STATUS['wsrep_local_state_comment'] == "Synced":

        print "status OK\n" \
            "metric WSREP_REPLICATED_BYTES int " \
            + SLAVE_STATUS["wsrep_replicated_bytes"]  + "\n"\
            "metric WSREP_RECEIVED_BYTES int " \
            + SLAVE_STATUS["wsrep_received_bytes"]  + "\n"\
            "metric WSREP_COMMIT_WINDOW float " \
            + SLAVE_STATUS["wsrep_commit_window"] + "\n" \
            "metric WSREP_CLUSTER_SIZE int " \
            + SLAVE_STATUS["wsrep_cluster_size"]