#!/usr/bin/env python

import collections
import time

from heatclient import exc
from maas_common import (get_heat_client, metric, metric_bool, status_err,
                         status_ok)

HEAT_STATUS = ['COMPLETE', 'FAILED', 'IN_PROGRESS']


def check_availability():
    """Check the availability of the Heat Orchestration API.

    Metrics include stacks built from either heat or cfn templates.
    Outputs metrics on current status of Heat and time elapsed during query.
    Outputs an error status if any error occurs querying Heat.
    Exits with 0 if Heat is available and responds with 200, otherwise 1.
    """

    try:
        heat = get_heat_client()

        counters = collections.Counter(zip(HEAT_STATUS,
                                           [0] * len(HEAT_STATUS)))
        start_at = time.time()
        for stack in heat.stacks.list():
            counters[stack.status] += 1
        elapsed_ms = (time.time() - start_at) * 1000

        status_ok()
        metric_bool('heat_api_global_status', True)
        for key in HEAT_STATUS:
            metric('heat_{0}_stacks'.format(key.lower()), 'uint32',
                   counters[key])
        metric('heat_response_ms', 'uint32', elapsed_ms)
    except exc.HTTPException:
        status_ok()
        metric_bool('heat_api_global_status', False)
    except Exception as e:
        status_err(str(e))


def main():
    check_availability()

if __name__ == "__main__":
    main()
