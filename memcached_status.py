#!/usr/bin/env python
import os
import re
import socket
import subprocess
import telnetlib


ITEM_COUNT = re.compile('STAT items:\d+:number (\d+)')


def item_stats(host, port):
    """Check the stats for items and connection status."""
    try:
        c = telnetlib.Telnet(host, port)
    except socket.error:
        return None
    c.write('stats items\r\n')
    results = c.read_until('END').strip('END')
    c.close()
    return results


def item_count(results):
    """Find the number of items in the cache."""
    if not results:
        return 0

    count = 0
    for result in results.split('\r\n'):
        m = ITEM_COUNT.match(result)
        if m is None:
            continue
        count += int(m.groups()[0], base=10)

    return count


def main():
    if not os.path.exists('/usr/bin/memcached'):
        return

    bind_ip = '127.0.0.1'
    port = 11211

    if os.path.exists('/etc/memcached.conf'):
      conf = open('/etc/memcached.conf')
      for line in conf:
        line_arr = line.split()

        if len(line_arr) > 1:
          if line_arr[0] == "-l":
            bind_ip = line_arr[1]
          elif line_arr[0] == "-p":
            port = line_arr[1]
      conf.close()

    results = item_stats(bind_ip, port)

    if results is not None:
        print 'status ok memcached is reachable'
        print 'metric items_in_cache {0}'.format(item_count(results))
    else:
        print 'status err memcached is unreachable'


if __name__ == '__main__':
    main()
