#!/usr/bin/env python

from rackspace_monitoring.drivers.rackspace import RackspaceMonitoringValidationError
from rackspace_monitoring.providers import get_driver
from rackspace_monitoring.types import Provider

import ConfigParser
import argparse
import sys


def main(args):
    config = ConfigParser.RawConfigParser()
    config.read('/root/.raxrc')

    driver = get_driver(Provider.RACKSPACE)
    conn = get_conn(config, driver)

    if conn is None:
        print("Unable to get a client to MaaS, exiting")
        sys.exit(1)

    for entity in conn.list_entities():
        error = 0
        if args.prefix is None or args.prefix in entity.label:
            for check in conn.list_checks(entity):
                try:
                    result = conn.test_existing_check(check)
                except RackspaceMonitoringValidationError as e:
                    print('Entity %s (%s):' % (entity.id, entity.label))
                    print(' - %s' % e)
                    break

                available = result[0]['available']
                status = result[0]['status']

                if available is False or status != 'okay':
                    if error == 0:
                        print('Entity %s (%s):' % (entity.id, entity.label))
                        error = 1
                    if available is False:
                        print(' - Check %s (%s) did not run correctly' %
                              (check.id, check.label))
                    elif status != 'okay':
                        print(" - Check %s (%s) ran correctly but returned a "
                              "'%s' status" % (check.id, check.label, status))


def get_conn(config, driver):
    conn = None

    if config.has_section('credentials'):
        try:
            user = config.get('credentials', 'username')
            api_key = config.get('credentials', 'api_key')
        except Exception as e:
            print e
        else:
            conn = driver(user, api_key)
    if not conn and config.has_section('api'):
        try:
            url = config.get('api', 'url')
            token = config.get('api', 'token')
        except Exception as e:
            print e
        else:
            conn = driver(None, None, ex_force_base_url=url,
                          ex_force_auth_token=token)

    return conn


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test MaaS checks')
    parser.add_argument('--prefix',
                        type=str,
                        help='Limit testing to checks on entities labelled w/ '
                             'this prefix',
                        default=None)
    args = parser.parse_args()

    main(args)
