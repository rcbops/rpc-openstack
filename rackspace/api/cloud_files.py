import json
import logging

import requests

from openstack_dashboard.api.base import APIDictWrapper
from rackspace.cloud_files.utils import convertSize # FIXME use template filter instead


# cloudFiles is pretty much equivalent to swift.  Rather than rewrite the swift stuff, let's
# try and re-use some code
from openstack_dashboard.api.swift import PseudoFolder, StorageObject, _objectify
from rackspace.api import AuthDetails


LOG = logging.getLogger(__name__)

class Container: # FIXME: Confirm that the original swift api Container class is not suitable.
    def __init__(self, name, region, files, size):
        self.id = name
        self.container_name = name
        self.region = region
        self.files = files
        self.size = size



def create_container(session, name):
    # Create a container
    auth_details = AuthDetails(request.session)
    url = auth_details.cloudFiles['defaultURL'] + '/' + name # FIXME - should allow choice of region
    # also ignoring private setting

    headers = {
        "Content-type":"application/json", 
        "X-Auth-Token":auth_details.token['id']
    }


    create_request = requests.put(
        url,
        headers=headers
    )

def get_containers(endpoint, token):
    # Given an endpoint url and an auth token return a list of all the containers
    containers = []
    
    headers = {
        "Content-type":"application/json", 
        "X-Auth-Token":token
    }

    url = endpoint['publicURL']
    LOG.debug("Getting containers for %s", url)
    try:
        r = requests.get(
            url,
            headers=headers,
            timeout=5
        )

        if r.content:
            for c in r.content.split('\n')[:-1]:
                container_url = url + '/' + c

                LOG.debug("Getting details for %s", container_url)
                
                try:
                    container_details = requests.head(container_url, headers=headers, timeout=5)
                
                    file_count = container_details.headers['x-container-object-count']
                    file_size = convertSize(int(container_details.headers['x-container-bytes-used']))

                    containers.append(Container(c, endpoint['region'], file_count, file_size))
                except requests.exceptions.SSLError:
                    LOG.error('Could not retrieve container details from %s because of an SSL error', url)
    except requests.exceptions.SSLError:
        LOG.error('Could not retrieve containers from %s because of an SSL error', url)

    return containers

def get_container_details(request, container, endpoint=None):
    auth_details = AuthDetails(request)

    headers = {
        "Content-type":"application/json", 
        "X-Auth-Token":auth_details.token['id'],
        "Accept":"application/json"
    }

    if not endpoint:
        endpoint = auth_details.cloudFiles['defaultURL']

    url = "{endpoint}/{container}".format(
        endpoint=endpoint, 
        container=container
    )

    req = requests.get(url, headers=headers)

    details = json.loads(req.content)