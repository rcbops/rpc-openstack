The user variables files for RPCO are broken out into the following:

-  ``user_osa_variables_defaults.yml`` - This file contains any
   variables specific to the OpenStack-Ansible project that are
   overridden and are now the default values for RPCO deployments.
   This file should not be modified by deployers.

-  ``user_rpco_variables_defaults.yml`` - This file contains RPCO
   variables that are exclusive to the RPCO playbooks and roles. i.e.
   rpc\_maas, rpc-support. The values defined in here will be used for
   RPCO deployments by default. This file should not be modified by
   deployers.

-  ``user_osa_variables_overrides.yml`` - Any OpenStack-Ansible variable
   that needs to be overridden by the deployer can be specified in this
   file.

-  ``user_rpco_variables_overrides.yml`` - Any RPCO specific variable
   that needs to be overridden by the deployer can be specified in this
   file.

-  ``user_rpco__secrets.yml`` - This file contains RPCO specific
   variables that are used as passwords, keys, or tokens. These values
   are populated by running the ``pw-token-gen.py`` script in the
   OpenStack-Ansible ``scripts/`` directory. For example:

::

    cd /opt/rpc-openstack/openstack-ansible/scripts && ./pw-token-gen.py --file /etc/openstack_deploy/user_rpco_secrets.yml

-  ``conf.d/ceph.yml.aio`` - This file contains target host
   configurations for an AIO ceph infrastructure. It defines ceph
   monitor hosts, osds hosts, and storage hosts for an AIO ceph
   deployment. For more information, please see
   https://pages.github.rackspace.com/rpc-internal/docs-rpc/rpc-install-internal/ch-ceph.html#deploy-ceph

-  ``env.d/``
    -  ``ceph.yml`` - Container groups and service mappings for the ceph software components are defined here.
    -  ``elasticsearch.yml`` - Container groups and service mappings for the elasticsearch software components are defined here.
    -  ``kibana.yml`` - Container groups and service mappings for the kibana software components are defined here.
    -  ``logstash.yml`` - Container groups and service mappings for the logstash software components are defined here.
    -  ``nova.yml`` - This file is copied over to /etc/openstack\_deploy/ and overrides the service mappings for the ``nova_compute_container`` group. This is due to the way OSA creates these group/service mappings to account for the openvswitch service. Since RPCO does not support openvswitch, there is a need to override this group/service mapping so the neutron agent containers do not get associated with the ``nova_compute_container`` group. For information please see https://bugs.launchpad.net/openstack-ansible/+bug/1645979

For more information about understanding container groups, please see
http://docs.openstack.org/project-deploy-guide/openstack-ansible/newton/app-custom-layouts.html
