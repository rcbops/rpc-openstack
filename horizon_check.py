#!/usr/bin/env python

import requests
import re
import maas_common
import sys
from requests import exceptions as exc
from lxml import html

HORIZON_URL = 'https://127.0.0.1'
HORIZON_PORT = '443'


def main():

    splash_status_code = 0
    splash_seconds = 0.0
    login_status_code = 0
    login_seconds = 0.0

    auth_details = maas_common.get_auth_details()
    OS_USERNAME = auth_details['OS_USERNAME']
    OS_PASSWORD = auth_details['OS_PASSWORD']

    s = requests.Session()

    try:
        r = s.get('%s:%s' % (HORIZON_URL, HORIZON_PORT),
                  verify=False,
                  timeout=10)

        splash_status_code = r.status_code
        splash_seconds = r.elapsed.total_seconds()
        if (r.status_code == requests.codes.ok and
                re.search('openstack dashboard', r.content, re.IGNORECASE)):
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
            l = s.post(
                ('%s:%s/auth/login/') % (HORIZON_URL, HORIZON_PORT),
                data=payload,
                verify=False)
            login_status_code = l.status_code
            login_seconds = l.elapsed.total_seconds()
            if (l.status_code == requests.codes.ok and
                    re.search('overview', l.content, re.IGNORECASE)):
                print 'status OK'
            else:
                print 'status err could not log in'
                sys.ext(1)
        else:
            print 'status err could not load login page'
            sys.ext(1)

    except (exc.ConnectionError,
            exc.HTTPError,
            exc.Timeout) as e:
        print 'status err %s ' % e

    print 'metric splash_status_code uint32 %d' % splash_status_code
    print 'metric splash_seconds double %.2f' % splash_seconds
    print 'metric login_status_code uint32 %d' % login_status_code
    print 'metric login_seconds double %.2f' % login_seconds

if __name__ == "__main__":
    main()
