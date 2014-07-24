#!/usr/bin/env python
import json
import requests

ES_HOST = 'localhost'
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
    latest = find_indices()[-1]
    num_errors = get_number_of('ERROR', latest)
    num_warnings = get_number_of('WARN*', latest)
    print 'metric int NUMBER_OF_LOG_ERRORS {0}'.format(num_errors)
    print 'metric int NUMBER_OF_LOG_WARNINGS {0}'.format(num_warnings)


if __name__ == '__main__':
    main()
