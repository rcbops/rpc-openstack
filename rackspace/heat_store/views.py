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

# from django.views.generic import TemplateView
from horizon.tables import DataTableView
from rackspace.heat_store.catalog import Catalog
from rackspace.heat_store import tables

# import yaml


class IndexView(DataTableView):
    table_name = tables.TemplateTable
    template_name = 'rackspace/heat_store/index.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        context['templates'] = load_templates()
        return self.render_to_response(context)

    def get_tables(self):
        return dict((t.title, t) for t in load_templates())


def load_templates():
    c = Catalog(
        '../RAX_SPOG/rackspace/heat_store/catalog/test_data/catalog.yml'
    )
    return c
    # with open('../RAX_SPOG/templates/drupal/info.yaml') as fd:
    #     template = yaml.safe_load(fd)

    # templates = []
    # for i in range(20):
    #     t = template.copy()
    #     t['template_id'] = 'drupal-{0}'.format(i)
    #     templates.append(t)

    return templates
