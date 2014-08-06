#!/usr/bin/env python
import json
import os
import re
import requests

from maas_common import metric, status_ok, status_err


def get_elasticsearch_bind_host():
    """Get the bindhost for elasticsearch if we can read the config."""
    config = '/etc/elasticsearch/elasticsearch.yml'
    if not os.path.exists(config):
        return 'localhost'

    with open(config) as fd:
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


def json_querystring(query_string, sort=None):
    """Generate the JSON data for a query_string query."""
    query_dict = {'query': {'query_string': query_string}}
    if sort:
        query_dict['sort'] = sort
    return json.dumps(query_dict)


def json_filter(filtered_query):
    """Generate the JSON data for a filtered query."""
    return json.dumps({'query': {'filtered': filtered_query}})


def find_indices():
    """Find indices created by logstash."""
    url = ELASTICSEARCH + '/_search'
    query = json_querystring({'query': '_index like logstash%'},
                             [{'_index': {'order': 'desc'}}])
    json = get_json(url, query)
    return sorted(res['_index'] for res in json['hits']['hits'])


def most_recent_index():
    """Get the most recent index if one indeed exists."""
    indices = find_indices()

    if not indices:
        status_err('There are no elasticsearch indices to search')

    return indices[-1]


def search_url_for(index):
    """Generate the search URL for an index."""
    return ELASTICSEARCH + '/' + index + '/_search'


def get_json(url, data):
    """Wrap calls to requests to handle exceptions."""
    exceptions = (requests.exceptions.HTTPError,
                  requests.exceptions.ConnectionError)
    try:
        r = requests.get(url, data=data)
    except exceptions as e:
        status_err(str(e))

    return r.json()


def get_number_of(loglevel, index):
    """Retrieve the number of logs with level ``loglevel``."""
    url = search_url_for(index)
    data = json_querystring({'query': loglevel,
                             'fields': ['os_level', 'message']})
    json = get_json(url, data)
    return json['hits']['total']


def main():
    latest = most_recent_index()
    num_errors = get_number_of('ERROR', latest)
    num_warnings = get_number_of('WARN*', latest)

    status_ok()
    metric('NUMBER_OF_LOG_ERRORS', 'uint32', num_errors)
    metric('NUMBER_OF_LOG_WARNINGS', 'uint32', num_warnings)


if __name__ == '__main__':
    main()
