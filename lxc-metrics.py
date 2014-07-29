#!/usr/bin/env python
import sys
import subprocess
import optparse

from maas_common import status_err, status_ok, metric


def retrieve_stats(path, metric, container=None):
    new_path = path + '/' + metric + '/lxc/'
    if container:
        new_path = new_path + container

    if metric == 'memory':
        slab = new_path + '/memory.stat'
    if metric == 'cpu':
        slab = new_path + '/cpu.stat'

    command = '/bin/cat ' + slab
    p = subprocess.Popen(command, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True)

    stdout, stderr = p.communicate()

    if stderr:
        return None, stderr

    stdout = stdout.split('\n')
    return stdout


def parse_metrics(metrics):
    del metrics[-1]

    metric_list = {}
    for i in metrics:
        metric_list[i.split(' ')[0]] = i.split(' ')[1]

    return metric_list

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('--path', action='store',
                      dest='lxc_cgroup_path',
                      default='/sys/fs/cgroup',
                      help="Path to lxc cgroup directories")
    parser.add_option('--metric', action='store',
                      dest='metric',
                      help="Which metric to get (cpu, memory)")
    parser.add_option('--system', action='store_true',
                      dest='system',
                      help="Retreive overall lxc cgroup metrics")
    parser.add_option('--container', action='store',
                      dest='container',
                      help='Get metrics by container <name>')

    (options, args) = parser.parse_args(sys.argv)

    cgroup_path = options.lxc_cgroup_path
    sys = options.system
    cont = options.container

    if not options.metric:
        status_err('missing required argument: metric')

    if not sys and not cont:
        status_err('neither system or container was defined')

    metrics = retrieve_stats(cgroup_path, options.metric, cont)
    metrics_list = parse_metrics(metrics)

    status_ok()
    for k, v in metrics_list.iteritems():
        metric(k, 'int64', v)
