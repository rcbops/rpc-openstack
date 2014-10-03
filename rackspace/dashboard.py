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

import horizon


class RackspacePanelGroup(horizon.PanelGroup):
   slug = 'rackspace_private_cloud'
   name = 'Rackspace Private Cloud'
   panels = ('welcome', 'training', )

class RackspacePublicCloudGroup(horizon.PanelGroup):
   slug = 'rackspace_public_cloud'
   name = 'Rackspace Public Cloud'
   panels = ('public_cloud', 'cloud_files')

class RackspaceDashboard(horizon.Dashboard):
   name = 'Rackspace'
   slug = 'rackspace'
   panels = (RackspacePanelGroup, RackspacePublicCloudGroup)
   default_panel = 'welcome'

horizon.register(RackspaceDashboard)
