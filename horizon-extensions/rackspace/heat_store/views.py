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

import os
import json

from django.core import urlresolvers
from django.views.generic.base import View
from django.http import HttpResponse, HttpResponseBadRequest
from horizon.tables import DataTableView

from rackspace.heat_store.catalog import Catalog
from rackspace.heat_store import tables


RAX_CONFIG = '/etc/rackspace/solutions.yaml'
USER_CONFIG = '/etc/rackspace/solutions-user.yaml'


class IndexView(DataTableView):
    table_class = tables.TemplateTable
    template_name = 'rackspace/heat_store/index.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        tables = []
        for (name, table) in list(context.items()):
            if name.endswith('_table'):
                del context[name]
                table.data.parameters = json.dumps(
                    table.data.get_parameter_types(self.request))
                table.data.launch_url = urlresolvers.reverse(
                    'horizon:rackspace:heat_store:launch',
                    args=[table.data.id])
                tables.append(table)

        context['tables'] = tables
        return self.render_to_response(context)

    def get_tables(self):
        return dict((t.title, self.table_class(self.request, t))
                    for t in load_templates())


class LaunchView(View):
    pattern_name = 'horizon:project:stacks:index'

    def post(self, request, *args, **kwargs):
        catalog = load_templates()
        template_id = kwargs['template_id']
        template = catalog.find_by_id(template_id)
        if template is None:
            return HttpResponseBadRequest('Solution not found.')
        args = json.loads(request.body)
        if not template.launch(request, args):
            return HttpResponseBadRequest('Heat failed to launch template.')
        return HttpResponse(urlresolvers.reverse(self.pattern_name))


def load_templates():
    catalogs = []
    if os.path.isfile(RAX_CONFIG):
        catalogs.append(RAX_CONFIG)
        if os.path.isfile(USER_CONFIG):
            catalogs.append(USER_CONFIG)
    else:
        basedir = os.path.abspath(os.path.dirname(__file__))
        catalogs.append(os.path.join(basedir, 'catalog/test_data/catalog.yml'))
    return Catalog(*catalogs)
