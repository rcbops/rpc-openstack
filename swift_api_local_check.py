#!/usr/bin/env python

from time import time
from maas_common import (status_ok, status_err, metric, metric_bool,
                         get_auth_ref, get_keystone_client)

try:
    from swiftclient import client
    from swiftclient.exceptions import ClientException
except Exception as e:
    # no swift client, exit with error
    status_err(str(e))


def check(auth_ref):
    status_msg = None
    api_is_up = True
    elapsed = -1

    keystone = get_keystone_client(auth_ref)
    if keystone is None:
        status_err('Unable to obtain valid keystone client')

    endpoint = keystone.service_catalog.url_for(
        service_type='object-store', endpoint_type='publicURL')
    auth_token = keystone.auth_ref['token']['id']

    try:
        swift = client.Connection(preauthurl=endpoint, preauthtoken=auth_token)
        if swift is None:
            status_msg = 'Unable to obtain valid swift client'
            api_is_up = False
        else:
            # make a simple call to make sure everything works
            start = time()
            swift.get_account()
            elapsed = int((time() - start) * 1000)

    except ClientException as e:
        status_msg = str(e)
        api_is_up = False

    except Exception as e:
        # unknown exception, exit with error
        status_err(str(e))

    status_ok(status_msg)
    metric_bool('swift_api_local_status', api_is_up)
    metric('swift_api_response_time', 'int32', elapsed)


def main():
    auth_ref = get_auth_ref()
    check(auth_ref)


if __name__ == "__main__":
    main()
