# Copyright 2014 Rackspace
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import tables

from openstack_dashboard import api
import tables as project_tables


class AdminCreateContainer(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Container")
    url = "horizon:rackspace:cloud_files:create"
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("image", "add_container"),)



#class AdminDeleteCloudFile(project_tables.DeleteCloudFile):
    #def allowed(self, request, image=None):
        #return True


#class AdminEditCloudFile(project_tables.EditCloudFile):
    #url = "horizon:admin:images:update"

    #def allowed(self, request, image=None):
        #return True


class UpdateRow(tables.Row):
    ajax = True

    #def get_data(self, request, image_id):
        #image = api.glance.image_get(request, image_id)
        #return image


class ContainersTable(tables.DataTable):
    container_name = tables.Column("container_name",
                         link="horizon:rackspace:cloud_files:detail",
                         verbose_name=_("Container Name"))

    region = tables.Column("region",
                         verbose_name=_("Region"))
    files= tables.Column("files",
                         verbose_name=_("Files"))
    size = tables.Column("size",
                         verbose_name=_("Size"))

    class Meta:
        name = "cloud_files"
        row_class = UpdateRow
        #status_columns = ["status"]
        verbose_name = _("Containers")
        table_actions = (AdminCreateContainer, )
        #row_actions = (AdminEditCloudFile, AdminDeleteCloudFile)


