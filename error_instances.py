#!/usr/bin/env python
#
# Copyright 2012, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys
from nova import config
from nova import context
from nova.conductor import api
from nova.openstack.common.rpc import impl_kombu, common

def main(hosts):
    # not entirely sure what happens here, but once this is
    # run we have access to all the CONF keys/values
    config.parse_args([])
    conductor_api = api.API()
    #ctxt = context.RequestContext(user_id="admin", project_id="admin",
    #                              is_admin=True)
    ctxt = context.get_admin_context()

    # can't filter by {'host': None} for whatever reason :-/
    filters = {'vm_state': 'error'}

    if hosts == 'one':
        filters['host'] = api.CONF.host

    try:
        instances = conductor_api.instance_get_all_by_filters(ctxt, filters)
    except common.Timeout:
        print "status timeout"
        sys.exit(1)

    count = 0

    for i in instances:
        # we skip these instances as they'll be accounted for when run from
        # the compute node
        if hosts == "all" and i['host'] is not None:
            continue

        count += 1

    print "status success"
    print "metric error int32 %d" % count
    #print "metric error int32 10"

if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] in ('all', 'one'):
            hosts = sys.argv[1]
        else:
            print "status invalid argument"
            sys.exit(1)

        main(hosts)
