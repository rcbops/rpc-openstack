#!/usr/bin/env python

from maas_common import get_nova_client, status_err, status_ok, metric_bool
from novaclient.client import exceptions as exc

COMPUTE_ENDPOINT = 'http://127.0.0.1:8774/v3'


def check():

    try:
        get_nova_client(bypass_url=COMPUTE_ENDPOINT)
        status_ok()
        metric_bool('nova_api_local_status', True)

    # if we get a ClientException don't bother sending any other metric
    # The API IS DOWN
    except exc.ClientException:
        metric_bool('nova_api_local_status', False)
    # Any other exception presumably isn't an API error
    except Exception as e:
        status_err(str(e))


def main():
    check()


if __name__ == "__main__":
    main()
