import re
import subprocess


def get_namespace_list():
    """Retrieve the list of DHCP namespaces."""
    return subprocess.check_output(['ip', 'netns', 'list']).split()


def get_interfaces_for(namespace):
    """Retrieve the list of interfaces inside a namespace."""
    return subprocess.check_output([
        'ip', 'netns', 'exec', namespace, 'ip', 'a'
    ]).split('\n')


def main():
    TAP = re.compile('^\d+: .*state [A-Z]+$')
    LOOP = re.compile('^\d+: lo')
    namespaces = get_namespace_list()
    if not namespaces:
        print 'status err no dhcp namespaces on this host'
        raise SystemError(True)

    interfaces = ((n, get_interfaces_for(n)) for n in namespaces)
    errored = False
    for namespace, interface_list in interfaces:
        # Filter down to the output of ip a that looks like 1: lo
        named_interfaces = filter(lambda i: TAP.match(i), interface_list)
        num_taps = len(i for i in named_interfaces if not LOOP.match(i))
        if num_taps != 1:
            print 'status err namespace {0} has {1} TAPs present'.format(
                namespaces, num_taps)
            errored = True

    if not errored:
        print 'status ok'
    else:
        raise SystemError(True)


if __name__ == '__main__':
    main()
