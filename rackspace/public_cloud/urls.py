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

from django.conf.urls import patterns, url

from rackspace.public_cloud.views import (
    IndexView, RPCLoginView, login, logged_in, logout
    )

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^rpclogin$', login, name='rpclogin'),
    url(r'^rpclogout$',logout, name='logout'),
    url(r'^logged_in$', logged_in, name='logged_in')
)
