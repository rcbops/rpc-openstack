import json
import re
import requests
import subprocess


def get_elasticsearch_container():
    containers = subprocess.check_output('lxc-ls').strip().split('\n')
    for container in containers:
        if 'elasticsearch' in container:
            break
    else:
        raise SystemExit(True)

    return container


def get_elasticsearch_address():
    """Get the bind_host address from elasticsearch's config."""
    es_container = get_elasticsearch_container()
    cmd = ['lxc-attach', '-n', es_container, '--', 'cat',
           '/etc/elasticsearch/elasticsearch.yml']
    output = subprocess.check_output(cmd)
    match = re.search('network\.bind_host:\s+([0-9\.]+)\s+', output)
    return match.groups()[0]


def find_indices(address):
    """Find indices created by logstash."""
    url = 'http://{0}:9200/_search'.format(address)
    r = requests.get(url, params={'_q': '_index like logstash%'})
    return sorted(res['_index'] for res in r.json()['hits']['hits'])


def get_number_of(loglevel, address, index):
    """Retrieve the number of logs with level ``loglevel``."""
    url = 'http://{0}:9200/{1}/_search'.format(address, index)
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
    address = get_elasticsearch_address()
    latest = find_indices(address)[-1]
    num_errors = get_number_of('ERROR', address, latest)
    num_warnings = get_number_of('WARN*', address, latest)
    print 'metric int NUMBER_OF_LOG_ERRORS {0}'.format(num_errors)
    print 'metric int NUMBER_OF_LOG_WARNINGS {0}'.format(num_warnings)


if __name__ == '__main__':
    main()
