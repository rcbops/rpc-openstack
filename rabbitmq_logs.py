import optparse

from maas_common import metric, status_ok, status_err

from elasticsearch import (
    most_recent_index, json_filter, search_url_for, get_json
)


def search_for_loglevel(loglevel, index=None):
    index = index or most_recent_index()
    query_string = 'ampq_{0} {1}'.format(loglevel.lower(), loglevel.upper())
    query = json_filter({
        'query': {'query_string': {'query': query_string}},
        'filter': {'query': {'query_string': {'query': 'rabbit'}}}
    })
    url = search_url_for(index)
    return get_json(url, query)


def search_for_errors(index=None):
    return search_for_loglevel('error', index)


def search_for_warnings(index=None):
    return search_for_loglevel('warning', index)


def parse_args():
    parser = optparse.OptionParser(usage='%prog [-h|--help] [-i index]')
    parser.add_option('-i', '--index', action='store', dest='index',
                      default=None,
                      help='Use specified index instead of latest')
    return parser.parse_args()


def main():
    options, _ = parse_args()

    errors = search_for_errors(options.index)
    warnings = search_for_warnings(options.index)

    if 'hits' in errors:
        status_ok()
        metric('rabbitmq_logs_errors', 'uint32', errors['hits']['total'])
    elif 'error' in errors:
        status_err(errors['error'])
    else:
        status_err('Something went wrong searching for rabbitmq logs')

    if 'hits' in warnings:
        metric('rabbitmq_logs_warnings', 'uint32', warnings['hits']['total'])


if __name__ == '__main__':
    main()
