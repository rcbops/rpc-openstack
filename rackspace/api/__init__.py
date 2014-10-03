# Copyright 2014, Rackspace US, Inc.
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
# limitations under the License

import json

from horizon import exceptions

class RPCNotAuthenticated(exceptions.NotAuthenticated):
    """Used to distinguish NotAuthenticated errors in the RAX_SPOG from the normal horizon NotAuthenticated exception"""
    pass

class AuthDetails:
    def __init__(self, request):
        
        auth_details = request.session.get('rax_auth')
        
        if not auth_details:
            raise RPCNotAuthenticated
        
        auth_details = json.loads(auth_details)
        
        self.token = auth_details['access']['token']
        self.serviceCatalog = auth_details['access']['serviceCatalog']
        self.user = auth_details['access']['user']
        
        for i in range(len(self.serviceCatalog)):
            self.__dict__[self.serviceCatalog[i]['name']] = self.serviceCatalog[i]
            self.__dict__[self.serviceCatalog[i]['name']]['defaultURL'] = \
                self.__dict__[self.serviceCatalog[i]['name']]['endpoints'][0]['publicURL']
            self.__dict__[self.serviceCatalog[i]['name']]['account'] = \
                self.__dict__[self.serviceCatalog[i]['name']]['endpoints'][0]['tenantId']
            # FIXME - assuming tenantId == account


    