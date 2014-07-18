import optparse
import subprocess


def table_checksum(user, password, host):
    args = ['/usr/bin/pt-table-checksum', '-u', user, '-p', password]
    if host:
        args.extend(['-h', host])

    proc = subprocess.Popen(args, stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    return (proc.return_code, out, err)


def main():
    usage = "Usage: %prog [-h] [-H] username password"

    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-H', '--host', action='store', dest='host',
                      default=None)
    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.print_help()
        raise SystemExit(True)

    (status, _, err) = table_checksum(args[0], args[1], options.host)
    if status != 0:
        print "status err %s" % err
        raise SystemExit(True)

    print "status ok"


if __name__ == '__main__':
    main()
