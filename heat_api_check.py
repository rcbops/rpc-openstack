#!/usr/bin/env python

import sys
import time

from heatclient.client import Client
from maas_common import get_heat_client
from maas_common import get_auth_ref
from maas_common import get_keystone_client
from maas_common import metric
from maas_common import status_err
from maas_common import status_ok

STATUS_COMPLETE = 'COMPLETE'
STATUS_FAILED = 'FAILED'
STATUS_IN_PROGRESS = 'IN_PROGRESS'


def check_availability(auth_ref):
    """Check the availability of the Heat Orchestration API.

    :param auth_ref: A Keystone auth token reference for use in querying Heat

    Metrics include stacks built from either heat or cfn templates.
    Outputs metrics on current status of Heat and time elapsed during query.
    Outputs an error status if any error occurs querying Heat.
    Exits with 0 if Heat is available and responds with 200, otherwise 1.
    """
    keystone = get_keystone_client(auth_ref)
    if keystone is None:
        status_err('Unable to obtain valid keystone client, cannot proceed')

    heat_endpoint = keystone.service_catalog.url_for(
        service_type='orchestration', endpoint_type='publicURL')
    auth_token_id = keystone.auth_ref['token']['id']
    heat = get_heat_client(heat_endpoint, auth_token_id)

    complete, failed, in_progress = 0, 0, 0
    start_at = time.time()
    try:
        for stack in heat.stacks.list():
            if STATUS_COMPLETE == stack.status:
                complete += 1
            if STATUS_FAILED == stack.status:
                failed += 1
            if STATUS_IN_PROGRESS == stack.status:
                in_progress += 1
    except Exception as e:
        status_err(str(e))
    elapsed_ms = (time.time() - start_at) * 1000

    status_ok('heat api success')
    metric('heat_complete_stacks', 'uint32', complete)
    metric('heat_failed_stacks', 'uint32', failed)
    metric('heat_in_progress_stacks', 'uint32', in_progress)
    metric('heat_response_ms', 'double', elapsed_ms)


def main():
    check_availability(get_auth_ref())

if __name__ == "__main__":
    main()
