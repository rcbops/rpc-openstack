#!/usr/bin/env python
import json
import re
import requests

from maas_common import metric


def get_elasticsearch_bind_host():
    with open('/etc/elasticsearch/elasticsearch.yml') as fd:
        contents = fd.readlines()
    bind_host_re = re.compile('^network\.bind_host:\s+([0-9\.]+)\s+')
    hosts = filter(bind_host_re.match, contents)
    if not hosts:
        raise SystemExit(False)
    match = bind_host_re.match(hosts[-1])
    return match.groups()[0]

ES_HOST = get_elasticsearch_bind_host()
ES_PORT = '9200'
ELASTICSEARCH = 'http://{0}:{1}'.format(ES_HOST, ES_PORT)


def find_indices():
    """Find indices created by logstash."""
    url = ELASTICSEARCH + '/_search'
    r = requests.get(url, params={'_q': '_index like logstash%'})
    return sorted(res['_index'] for res in r.json()['hits']['hits'])


def get_number_of(loglevel, index):
    """Retrieve the number of logs with level ``loglevel``."""
    url = ELASTICSEARCH + '/' + index + '/_search'
    r = requests.get(url, data=json.dumps({
        'query': {
            'query_string': {
                'query': loglevel,
                'fields': ['os_level', 'message']
            }
        }
    }))
    return r.json()['hits']['total']


def main():
    indices = find_indices()

    if not indices:
        return

    latest = indices[-1]
    num_errors = get_number_of('ERROR', latest)
    num_warnings = get_number_of('WARN*', latest)
    metric('NUMBER_OF_LOG_ERRORS', 'int', num_errors)
    metric('NUMBER_OF_LOG_WARNINGS', 'int', num_warnings)


if __name__ == '__main__':
    main()
