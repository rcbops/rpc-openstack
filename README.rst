RACKSPACE SPOG
##############
:date: 2013-09-26 09:51
:tags: Rackspace, Horizon, SPOG
:category: \*nix


Rackspace, installable Horizon SPOG.


THIS IS JUST A POC, NOT AN ACTUAL PRODUCT
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

THIS IS FOR DEMO PURPOSES ONLY!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

At present the plugin has no method for dynamically storing user credentials, This is hard coded in the ``auth_plugin.py`` module.


========

After you install you have to add the following lines to your settings file.

I recommend you add them to your local settings file which is generally located here: ``/etc/openstack-dashboard/local_settings.py``


.. code-block::

    import sys
    import rackspace
    mod = sys.modules['openstack_dashboard.settings']
    mod.INSTALLED_APPS += ('rackspace',)
    if 'STATICFILES_DIRS' in dir(mod):
        mod.STATICFILES_DIRS += (
            os.path.join(rackspace.__path__[0], 'static')
        )
    else:
        mod.STATICFILES_DIRS = (
            os.path.join(rackspace.__path__[0], 'static')
        )


If you are looking for the Rackspace Tab to be the default modify the horizon config as found in the ``/etc/openstack-dashboard/local_settings.py`` file.


.. code-block::

    HORIZON_CONFIG = {
        'dashboards': ('rackspace', 'project', 'admin', 'settings',),
        'default_dashboard': 'rackspace',
        'user_home': 'rackspace.views.get_user_home',
        'ajax_queue_limit': 10,
        'auto_fade_alerts': {
            'delay': 3000,
            'fade_duration': 1500,
            'types': ['alert-success', 'alert-info']
        },
        'help_url': "http://www.rackspace.com/knowledge_center/product-page/rackspace-private-cloud",
        'exceptions': {'recoverable': exceptions.RECOVERABLE,
                       'not_found': exceptions.NOT_FOUND,
                       'unauthorized': exceptions.UNAUTHORIZED},
    }



Then collect all your new **SPOG** files.


.. code-block::

    /usr/share/openstack-dashboard/manage.py collectstatic --noinput


Lastly, restart Apache2 and Memcached, provided you're running them.


.. code-block::

    service apache2 restart && service memcached restart


License
^^^^^^^

Copyright 2012, Rackspace US, Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.