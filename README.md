# rpc-extras
Optional add-ons for Rackspace Private Cloud

# os-ansible-deploy integration

The rpc-extras repo includes add-ons for the Rackspace Private Cloud product
that integrate with the 
[os-ansible-deploy](https://github.com/stackforge/os-ansible-deployment)
set of Ansible playbooks and roles.
These add-ons extend the 'vanilla' OpenStack environment with value-added
features that Rackspace has found useful, but are not core to deploying an
OpenStack cloud.

# Ansible Playbooks

* `horizon_extensions.yml` - rebrands the horizon dashboard for Rackspace,
as well as adding a Rackspace tab and a Solutions tab, which provides
Heat templates for commonly deployed applications.
* `rpc-support.yml` - provides holland backup service, support SSH key
distribution, custom security group rules, bashrc settings, and other
miscellaneous tasks helpful to support personnel.
* `setup-maas.yml` - deploys, sets up, and installs Rackspace
[MaaS](http://www.rackspace.com/cloud/monitoring) checks
for Rackspace Private Clouds.

# Ansible Roles

* `horizon_extensions`
* `module_import`
* `rpc_maas`
* `rpc_support`
