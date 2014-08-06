#!/usr/bin/env python

import argparse
from ipaddr import IPv4Address
import requests
import re
from maas_common import get_auth_details, metric, status_err, status_ok
from requests import exceptions as exc
from lxml import html


def check(args):
    splash_status_code = 0
    splash_milliseconds = 0.0
    login_status_code = 0
    login_milliseconds = 0.0

    auth_details = get_auth_details()
    OS_USERNAME = auth_details['OS_USERNAME']
    OS_PASSWORD = auth_details['OS_PASSWORD']
    HORIZON_URL = 'https://{ip}'.format(ip=args.ip)
    HORIZON_PORT = '443'

    s = requests.Session()

    try:
        r = s.get('%s:%s' % (HORIZON_URL, HORIZON_PORT),
                  verify=False,
                  timeout=10)
    except (exc.ConnectionError,
            exc.HTTPError,
            exc.Timeout) as e:
        status_err(str(e))

    if not (r.ok and
            re.search('openstack dashboard', r.content, re.IGNORECASE)):
        status_err('could not load login page')

    splash_status_code = r.status_code
    splash_milliseconds = r.elapsed.total_seconds() * 1000

    csrf_token = html.fromstring(r.content).xpath(
        '//input[@name="csrfmiddlewaretoken"]/@value')[0]
    region = html.fromstring(r.content).xpath(
        '//input[@name="region"]/@value')[0]
    s.headers.update(
        {'Content-type': 'application/x-www-form-urlencoded',
            'Referer': HORIZON_URL})
    payload = {'username': OS_USERNAME,
               'password': OS_PASSWORD,
               'csrfmiddlewaretoken': csrf_token,
               'region': region}
    try:
        l = s.post(
            ('%s:%s/auth/login/') % (HORIZON_URL, HORIZON_PORT),
            data=payload,
            verify=False)
    except (exc.ConnectionError,
            exc.HTTPError,
            exc.Timeout) as e:
        status_err('While logging in: %s' % e)

    if not (l.ok and re.search('overview', l.content, re.IGNORECASE)):
        status_err('could not log in')

    login_status_code = l.status_code
    login_milliseconds = l.elapsed.total_seconds() * 1000

    status_ok()
    metric('splash_status_code', 'uint32', splash_status_code)
    metric('splash_milliseconds', 'double', splash_milliseconds)
    metric('login_status_code', 'uint32', login_status_code)
    metric('login_milliseconds', 'double', login_milliseconds)


def main(args):
    check(args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check dashboard')
    parser.add_argument('ip',
                        type=IPv4Address,
                        help='dashboard IP address.')
    args = parser.parse_args()
    main(args)
