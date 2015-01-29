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

from django.core import urlresolvers
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from horizon.tables import DataTableView

from rackspace.heat_store.catalog import Catalog
from rackspace.heat_store import tables


class IndexView(DataTableView):
    table_class = tables.TemplateTable
    template_name = 'rackspace/heat_store/index.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        tables = []
        for (name, table) in list(context.items()):
            if name.endswith('_table'):
                del context[name]
                table.data.parameter_types = json.dumps(table.data.get_parameter_types(self.request))
                table.data.launch_url = urlresolvers.reverse('horizon:rackspace:heat_store:launch', args=[table.data.id])
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
        catalog = load_templates()
        template_id = context['template_id']
        context['template'] = catalog.find_by_id(template_id)
        context['hide'] = True
        context['launch_link'] = urlresolvers.reverse(
            'horizon:rackspace:heat_store:launch', args=[template_id]
        )
        return self.render_to_response(context)


class LaunchView(RedirectView):
    permanent = False
    pattern_name = 'horizon:project:stacks:index'

    def get_redirect_url(self, *args, **kwargs):
        catalog = load_templates()
        template_id = kwargs['template_id']
        template = catalog.find_by_id(template_id)
        if template is not None:
            print("Launching template {0}".format(template.id))
            template.launch(self.request)
        return urlresolvers.reverse(self.pattern_name)


def load_templates():
    import os
    basedir = os.path.abspath(os.path.dirname(__file__))
    return Catalog(
        os.path.join(basedir, 'catalog/test_data/catalog.yml')
    )


#def templates_as_json():
