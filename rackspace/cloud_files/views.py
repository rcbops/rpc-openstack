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
import requests

from django import forms
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from openstack_dashboard import settings

from horizon import exceptions
from horizon import tables
from horizon import forms as horizon_forms
from horizon.exceptions import Http302
from horizon.utils import memoized

import forms as project_forms
import tables as project_tables

from rackspace.api import RPCNotAuthenticated, AuthDetails
from rackspace.api.cloud_files import get_containers, get_container_details


class IndexView(tables.DataTableView):
    template_name = 'rackspace/cloud_files/index.html'
    table_class = project_tables.ContainersTable

    def has_more_data(self, table):
        return False # self._more

    def get(self, request, *args, **kwargs):
        try:
            self.auth_details = AuthDetails(self.request)
            return super(IndexView, self).get(request, *args, **kwargs)
        except RPCNotAuthenticated:
            return redirect(reverse('horizon:rackspace:public_cloud:rpclogin'))

    def get_data(self):
        containers = []
        filters = {'is_public': None}

        try:
            #marker = self.request.GET.get(
            #project_tables.AdminImagesTable._meta.pagination_param, None)
            marker = None

            for endpoint in self.auth_details.cloudFiles['endpoints']:
                containers += get_containers(endpoint, self.auth_details.token['id'])

        except Exception:
            self._more = False
            msg = _('Unable to retrieve container list.')
            exceptions.handle(self.request, msg)

        return containers


class CreateView(horizon_forms.ModalFormView):
    form_class = project_forms.CreateContainerForm
    template_name = 'rackspace/cloud_files/create.html'
    context_object_name = 'container'
    success_url = reverse_lazy('horizon:rackspace:cloud_files:index')

class ContainerDetailView(horizon_forms.ModalFormMixin, TemplateView):
    template_name = 'rackspace/cloud_files/container_detail.html'

    @memoized.memoized_method
    def get_object(self,container):
        try:
            return get_container_details(self.request, container)
        except RPCNotAuthenticated:
            redirect = reverse("horizon:rackspace:public_cloud:index")
            raise Http302(redirect)

        except Exception:
            redirect = reverse("horizon:project:containers:index")
            exceptions.handle(self.request,
                              _('Unable to retrieve details.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(ContainerDetailView, self).get_context_data(**kwargs)
        context['container'] = self.get_object(kwargs['container'])
        return context