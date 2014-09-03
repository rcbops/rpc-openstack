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

import requests

from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from openstack_dashboard import settings

import q # FIXME remove before prod release


class IndexView(TemplateView):
    template_name = 'rackspace/public_cloud/index.html'

    def get(self, request, *args, **kwargs):
        if not request.session.get('rpc_token'):
            rd = reverse("horizon:rackspace:public_cloud:rpclogin")
            return redirect(rd)
        
        context = self.get_context_data(**kwargs)
        context['rpc_username'] = request.session['rpc_user']
        click_through = getattr(settings, 'RAX_SPOG_VALUES')
        #if click_through is not None and isinstance(click_through, dict):
            #context['training_query'] = click_through.get('training_query', '')
            

        return self.render_to_response(context)
    
    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=20, label='Username')
    password = forms.CharField(widget=forms.PasswordInput)
    
    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            payload = {
                "auth":{
                    "passwordCredentials":{
                        "username":username,
                        "password":password
                    }
                }
            }
            
            headers = {"Content-type":"application/json"}

            r = requests.post(
                "https://identity.api.rackspacecloud.com/v2.0/tokens", 
                data=json.dumps(payload),
                headers=headers
            )
            
            q(r)
            
            content = json.loads(r.content)
            if 'unauthorized' in content:
                raise forms.ValidationError(_('Could not login using the supplied username and password'))            
            
            self.rax_auth_details = content
            
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        q('Processing POST')
        
        
        if form.is_valid():
#            request.session['rax_auth_details'] = form.rax_auth_details
            #request.session['nt1'] = 'xxx'
            request.session['rpc_token'] = form.rax_auth_details['access']['token']['id']
            request.session['rpc_user'] = form.rax_auth_details['access']['user']['name']
            request.session['nctest'] = json.dumps(form.rax_auth_details)
            #request.session.modified = True
            #request.session.save()
            return HttpResponseRedirect(reverse("horizon:rackspace:public_cloud:index"))

    else:
        form = LoginForm()
        
    return render(request, 'rackspace/public_cloud/login.html', {'form':form})

def logged_in(request):
    return render(request, 'rackspace/public_cloud/logged_in.html')

def logout(request):
    if 'rpc_token' in request.session:
        del(request.session['rpc_token'])
    return render(request, 'rackspace/public_cloud/logged_out.html')
    
class RPCLoginView(TemplateView):
    template_name = 'rackspace/public_cloud/login.html'

    def get(self, request, *args, **kwargs):
        print q(request.session.get('public_username'))
        
        context = self.get_context_data(**kwargs)
        click_through = getattr(settings, 'RAX_SPOG_VALUES')
        #if click_through is not None and isinstance(click_through, dict):
            #context['training_query'] = click_through.get('training_query', '')
            

        return self.render_to_response(context)

