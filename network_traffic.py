import collections
import re

# In the event we need more information, let's name the information
Interface = collections.namedtuple(
    'Interface',
    ('name',  # Interface name, e.g., veth1064K4
     # Receive information
     'rcv_bytes', 'rcv_packets', 'rcv_errs', 'rcv_drop', 'rcv_fifo',
     'rcv_frame', 'rcv_compressed', 'rcv_multicast',
     # Transmit information
     'tx_bytes', 'tx_packets', 'tx_errs', 'tx_drop', 'tx_fifo', 'tx_colls',
     'tx_carrier', 'tx_compressed',)
)

SPLIT_RE = re.compile(':?\s+')


def network_info():
    """Retrieve a list of Interface objects to use to report metrics."""
    with open('/proc/net/dev', 'r') as fd:
        # The first two lines of this file are not important to us
        lines = fd.readlines()[2:]

    return [Interface(*SPLIT_RE.split(l.strip())) for l in lines]


def as_kb(num_bytes):
    """Take the parsed number of bytes and return it converted to kb."""
    return int(num_bytes, base=10) / 1024


def rcv_kb(interface):
    return as_kb(interface.rcv_bytes)


def tx_kb(interface):
    return as_kb(interface.tx_bytes)


def main():
    """The heart of the program."""
    for interface in network_info():
        print 'metric {0}_KB_RECEIVED int32 {1}'.format(
            interface.name, rcv_kb(interface)
        )
        print 'metric {0}_KB_SENT int32 {1}'.format(
            interface.name, tx_kb(interface)
        )


if __name__ == '__main__':
    main()
