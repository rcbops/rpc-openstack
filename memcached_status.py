#!/usr/bin/env python
import os
import socket
import subprocess
import telnetlib


def can_connect(host, port):
    """Check that we can make a connection to Memcached."""
    try:
        c = telnetlib.Telnet(host, port)
    except socket.error:
        return False
    c.close()
    return True


def main():
    if not os.path.exists('/etc/init.d/memcached'):
        return

    hostname = subprocess.check_output('hostname').strip()
    localhost = '127.0.0.1'

    if can_connect(hostname, '11211') or can_connect(localhost, '11211'):
        print 'status ok memcached is reachable'
    else:
        print 'status err memcached is unreachable'


if __name__ == '__main__':
    main()
