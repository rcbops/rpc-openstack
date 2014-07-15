import re
import subprocess


def output(command):
    return subprocess.check_output(command).strip()


def hostname():
    """Return the name of the current host/node."""
    return output(['hostname'])


def cluster_status():
    """Return the status of the RabbitMQ cluster."""
    status = output(['rabbitmqctl', 'cluster_status'])
    i, j = status.find('['), status.rfind(']') + 1
    status = status[i:j].replace('\n', '')
    return re.sub('\s+', '', status)


def node_in_cluster(nodename, nodes):
    """Check that the current node is present in the list of nodes."""
    return any(nodename in node for node in nodes)


def node_in_running_set(nodename, running_nodes):
    """Check that the current node is listed in the set of running nodes."""
    return any(nodename in node for node in running_nodes)


def parse_status(status):
    """Parse the output of cluster_status."""
    parsed_status = {}
    # Statuses have {nodes,[...]},
    #               {running_nodes,[...]},
    #               {cluster_name,'...'},
    #               {partitions,[...]}
    # To get the existing nodes, we want to find strings between '{nodes' and
    # '{running_nodes'. To get the running nodes we want strings between,
    # '{running_nodes' and '{cluster_name'.
    matches = ['{nodes,', '{running_nodes,', '{cluster_name,']
    positions = [status.find(m) for m in matches]  # e.g., 20, 45, 70
    search_ranges = zip(positions, positions[1:])  # e.g., [(20, 45), (45, 70)]

    for i, key in enumerate(['nodes', 'running_nodes']):
        start, end = search_ranges[i]
        parsed_status[key] = re.findall("'([^']+)'",
                                        status[start:end])
    return parsed_status


def main():
    name = hostname()
    status = parse_status(cluster_status())

    if not node_in_cluster(name, status['nodes']):
        print 'status err Node {0} not present in RabbitMQ Cluster'.format(
            name)
    else:
        print 'status ok Node {0} present in RabbitMQ Cluster'.format(name)

    if not node_in_running_set(name, status['running_nodes']):
        print 'status err Node {0} not listed as running'.format(name)
    else:
        print 'status ok Node {0} listed as running'.format(name)
