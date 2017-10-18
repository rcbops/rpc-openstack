# Testing for Rackspace Private Cloud Powered by OpenStack

## Overview
RPCO is an integration of OpenStack-Ansible with logging (ELK), and Monitoring
(MaaS). RPCO testing is not designed to test the individual services, it is
designed to test the functionality of the whole platform.

The reason for this is that each service is tested by the appropriate upstream,
for example the deployment of Nova is tested in OSA, and the nova service itself
is tested in OpenStack.

### Build Types
* AIO: Single cloud instance build of containerised RPC deployment
* [MNAIO](https://github.com/openstack/openstack-ansible-ops/blob/master/multi-node-aio/README.rst):
  Single OnMetal instance that hosts VMs simulating multiple RPC nodes. Each vm
  contains multiple containers as it would on a physical deploy.

#### Actions
* Deploy: Deploy, Test
* Upgrade: Deploy, Test, Upgrade Test
* Leapfrog Upgrade: Deploy, Test, Leapfrog Upgrade, Test

#### Test Types
* [Tempest](https://github.com/openstack/tempest): Run a subset of OpenStack tempest tests.

## Notes
* Jenkins has a useful [categorised view](https://rpc.jenkins.cit.rackspace.net/view/AIO/),
  this breaks down the 90+ jobs into categories making finding relevant jobs
  much easier.
