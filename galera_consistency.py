import io
import optparse
import subprocess

from maas_common import status_err, status_ok


def table_checksum(user, password, host):
    """Run pt-table-checksum with the user, password, and host specified."""
    args = ['/usr/bin/pt-table-checksum', '-u', user, '-p', password]
    if host:
        args.extend(['-h', host])

    out = io.StringIO()
    err = io.StringIO()
    proc = subprocess.Popen(args, stderr=subprocess.PIPE)

    # Let's poll the process to make sure it finishes before we return from
    # this function.
    while proc.poll() is None:
        # Avoid the OS Pipe buffer from blocking the process
        (stdout, stderr) = proc.communicate()
        # Let's store the aggregated output in buffers
        out.write(stdout)
        err.write(stderr)

    # The process has terminated, let's get the rest of stdout/stderr
    (stdout, stderr) = proc.communicate()
    out.write(stdout)
    err.write(stderr)
    # At this point we have a valid return code and the full stdout, stderr
    # logs
    return (proc.return_code, out.getvalue(), err.getvalue())


def check_version():
    proc = subprocess.Popen(['/usr/bin/pt-table-checksum', '--version'],
                            stdout=subprocess.PIPE)
    output, _ = proc.communicate()  # Ignore the status code, that's always 1
    _, version = output.strip().split(' ')
    if version != '2.2.7':
        status_err('This script has only been tested against version 2.2.7.'
                   ' Found version %s installed instead.' % version)


def main():
    usage = "Usage: %prog [-h] [-H] username password"

    check_version()

    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        '-H', '--host',
        action='store',
        dest='host',
        default=None,
        help="Allow user to connect to something other than localhost"
    )
    (options, args) = parser.parse_args()

    # We will need the username and password to connect to the database
    if len(args) != 2:
        parser.print_help()
        raise SystemExit(True)

    # According to
    # http://www.percona.com/doc/percona-toolkit/2.2/pt-table-checksum.html
    # If the exit status is 0, everything is okay, otherwise the exit status
    # will be non-zero. We don't need stdout at the moment so we can discard
    # it. Stderr should contain any problems we run across.
    (status, _, err) = table_checksum(args[0], args[1], options.host)
    if status != 0:
        status_err(err.strip())
        raise SystemExit(True)

    status_ok()


if __name__ == '__main__':
    main()
