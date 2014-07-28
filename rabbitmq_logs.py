import datetime
import collections
from maas_common import metric
import os
import re

LOG_MESSAGE_RE = re.compile(
    '=(?P<level>[A-Z]+) REPORT=+ '
    '(?P<datetime>\d+-\w+-\d{4}::\d{2}:\d{2}:\d{2})'  # Parse the datetime
    '.*=+\n(?P<msg>.*)',
    re.MULTILINE
)

LOGDIR = '/var/log/rabbitmq'

INTERVAL_IN_MINUTES = 5
INTERVAL_DELTA = datetime.timedelta(0, INTERVAL_IN_MINUTES * 60, 0)
START_DATETIME = datetime.datetime.now()


def log_filenames(logdir=LOGDIR):
    """Generate the rabbitmq log filenames."""
    for filename in os.listdir(logdir):
        if 'sasl' not in filename and filename.endswith(('log', 'err')):
            yield os.path.join(logdir, filename)


def get_messages_from(filename):
    r"""Get a list of log messages from a log file.

    RabbitMQ generates logs of the format::

        \n
        ={LOGLEVEL} REPORT==== {DATEINFO}
        {LOGMESSAGE}
        \n

    So there are two ``\n`` between each message.
    """
    with open(filename) as fd:
        content = fd.read().strip()

    return content.split('\n\n')


def generate_parsed_messages():
    """Generate dictionaries of parsed log messages."""
    for filename in log_filenames():
        for message in get_messages_from(filename):
            m = LOG_MESSAGE_RE.match(message)
            if m:
                parsed = m.groupdict()
                parsed['datetime'] = datetime.datetime.strptime(
                    parsed['datetime'],
                    '%d-%b-%Y::%H:%M:%S'
                )
                yield parsed


def main():
    log_level_counter = collections.Counter()
    for message in generate_parsed_messages():
        level = message['level']
        log_level_counter.update((level,))
        if (level in ('ERROR', 'WARNING') and
                (START_DATETIME - message['datetime'] < INTERVAL_DELTA)):
            metric_name = 'rabbitmq_{0}_{1}'.format(level.lower(),
                                                    log_level_counter[level])
            metric(metric_name, 'string', message['msg'])

    for (level, count) in log_level_counter.items():
        metric('num_{0}'.format(level.lower()), 'uint32', count)


if __name__ == '__main__':
    main()
