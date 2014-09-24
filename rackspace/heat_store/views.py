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

from django.views.generic import TemplateView
from horizon.tables import DataTableView
from rackspace.heat_store.catalog import Catalog
from rackspace.heat_store import tables

# import yaml


class IndexView(DataTableView):
    table_class = tables.TemplateTable
    template_name = 'rackspace/heat_store/index.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        tables = []
        for (name, table) in list(context.items()):
            if name.endswith('_table'):
                del context[name]
                tables.append(table)

        context['tables'] = tables
        return self.render_to_response(context)

    def get_tables(self):
        return dict((t.title, self.table_class(self.request, t))
                    for t in load_templates())


class MoreInformationView(TemplateView):
    template_name = 'rackspace/heat_store/_modal.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        import pdb
        pdb.set_trace()
        catalog = load_templates()
        context['template'] = catalog.find_by_id()
        return self.render_to_response(context)


def load_templates():
    return Catalog(
        '../RAX_SPOG/rackspace/heat_store/catalog/test_data/catalog.yml'
    )
