#!/usr/bin/env python

from maas_common import (get_neutron_client,
                         status_err, status_ok, metric_bool)
from neutronclient.common import exceptions as exc

NETWORK_ENDPOINT = 'http://127.0.0.1:9696'


def check():

    try:
        get_neutron_client(endpoint_url=NETWORK_ENDPOINT)
        status_ok()
        metric_bool('neutron_api_local_status', True)

    # if we get a NeutronClientException don't bother sending any other metric
    # The API IS DOWN
    except exc.NeutronClientException:
        status_ok()
        metric_bool('neutron_api_local_status', False)
    # Any other exception presumably isn't an API error
    except Exception as e:
        status_err(str(e))


def main():
    check()


if __name__ == "__main__":
    main()
