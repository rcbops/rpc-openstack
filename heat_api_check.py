#!/usr/bin/env python

import sys
import time
import maas_common
from heatclient import Client, exc

STATUS_COMPLETE = 'COMPLETE'
STATUS_FAILED = 'FAILED'
STATUS_IN_PROGRESS = 'IN_PROGRESS'

def check_availability(auth_ref):
	"""Check the availability of the Heat Orchestration API.

	:param dict auth_ref: A Keystone auth token to use when querying Heat

	Outputs basic metrics on the current status of Heat and the time elapsed during query.
	Outputs an error status if any error occurs querying Heat.
	Exits with 0 if Heat is available and responds without error, otherwise 1.
	"""
	keystone = maas_common.get_keystone_client(auth_ref)
    if keystone is None:
        print 'status err Unable to obtain valid keystone client, ' \
              'cannot proceed'
        sys.exit(1)

    service = keystone.services.find(type='orchestration')
    endpoint = keystone.endpoints.find(service_id=service.id)
    os_heat_endpoint = endpoint.publicurl
    os_auth_token = keystone.auth_ref['token']['id']

    start_at = time.time()
    heat = Client('1', endpoint=os_heat_endpoint, token=os_auth_token)
    elapsed_ms = (time.time() - start_at) * 1000

    complete, failed, in_progress = 0, 0, 0
    for stack in heat.stacks.list():
    	if STATUS_COMPLETE == stack.status:
    		complete += 1
		if STATUS_FAILED == stack.status:
			sad += 1
    	if STATUS_IN_PROGRESS == stack.status:
    		in_progress += 1

	except (exc.CommunicationError,
            exc.HTTPInternalServerError,
            exc.HTTPUnauthorized) as e:
        print 'status err {0}'.format(e)
        sys.exit(1)

    print 'status heat api success'
    print 'metric heat_active_stacks uint32 {0}'.format(complete)
    print 'metric heat_killed_stacks uint32 {0}'.format(failed)
    print 'metric heat_queued_stacks uint32 {0}'.format(in_progress)
    print 'metric heat_response_ms double {0}'.format(elapsed_ms) 
