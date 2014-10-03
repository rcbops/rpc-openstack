# Copyright 2013, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import math

from rackspace.api import RPCNotAuthenticated

def convertSize(size):
    # FIXME - confirm that this code does not exist somewhere else in OpenStack
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
                
    if size:
        i = int(math.floor(math.log(size,1024)))
        p = math.pow(1024,i)
        s = round(size/p,2)
    else:
        return '0 KB'
                
    if (s > 0):
        return '%s %s' % (s,size_name[i])
    else:
        return '0B'

