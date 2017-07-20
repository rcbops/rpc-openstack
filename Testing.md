## Testing for Rackspace Private Cloud Powered by OpenStack

### Overview
RPCO is an integration of OpenStack-Ansible with logging (ELK), and Monitoring (MaaS). RPCO testing is not designed to test the individual services, it is designed to test the functionality of the whole platform.

The reason for this is that each service is tested by the appropriate upstream, for example the deployment of Nova is tested in OSA, and the nova service itself is tested in OpenStack.

#### Terms
* RPCO: Rackspace Private Cloud Powered by OpenStack (This repo.)
* OSA: OpenStack Ansible.
* [MaaS](https://www.rackspace.com/en-gb/cloud/monitoring): Monitoring as a Service
* ELK:
  * [Elasticsearch](https://www.elastic.co/products/elasticsearch): Search optimised DB
  * Logstash: Log shipper, RPCO uses [filebeat](https://www.elastic.co/products/beats) instead
  * [Kibana](https://www.elastic.co/products/kibana): Dashboard
* Periodic: Scheduled test against the head of a branch.
* Gate: Test that proposed changes must pass before they are merged into the target repository.
* PR: Github Pull Request, a set of changes proposed for merging into
a repo, which must first pass peer review and automated testing.
* [Jenkins](https://rpc.jenkins.cit.rackspace.net/): Continuous integration application used to run scheduled tests and PR gates.
* [rpc-gating](https://github.com:rcbops/rpc-gating): The repository where the release engineering team defines automated testing infrastructure.
* [Leapfrog](https://github.com/rcbops/rpc-openstack/blob/newton-14.1/scripts/leapfrog/README.md): Upgrade process that skips major versions
* [Selenium](http://www.seleniumhq.org/): Browser automation / UI test suite
* [Holland](http://hollandbackup.org/): Rackspace mysql backup tool.

#### Build Types
* AIO: Single cloud instance build of containerised RPC deployment
* [MNAIO](https://github.com/openstack/openstack-ansible-ops/blob/master/multi-node-aio/README.rst): Single OnMetal instance that hosts VMs simulating multiple RPC nodes. Each vm contains multiple containers as it would on a physical deploy.

#### Actions
* Deploy: Deploy, Test
* Upgrade: Deploy, Test, Upgrade Test
* Leapfrog Upgrade: Deploy, Test, Leapfrog Upgrade, Test

### Test Types
* [Tempest](https://github.com/openstack/tempest): Run a subset of OpenStack tempest tests.
* [Maas Verify Offline](https://github.com/rcbops/rpc-maas/blob/master/playbooks/files/rax-maas/tools/rpc-maas-tool.py#L397):
  * Syntax check MaaS alarm criteria
  * ensure metrics required by criteria are produced by plugins
  * Ensure plugins execute successfully
* MaaS Verify: Offline verify plus:
  * Ensure checks and alarms are registered with the MaaS API
  * Ensure check statuses are ok.
* [Kibana Selenium](https://github.com/rcbops-qe/kibana-selenium): Basic Browser tests to ensure the Kibana dashboard is worked as expected.
* [Holland](https://github.com/rcbops/rpc-gating/blob/master/playbooks/test_holland.yml): Basic test to ensure holland is configured correctly.
* [Horizon Selenium](https://github.com/rcbops-qe/horizon-selenium): Basic browser tests to ensure horizon is functioning.

#### Test Matrix
|                     | AIO | MNAIO | Tempest | Holland | Kibana Selenium | Horizon Selenium | MaaS | MaaS Offline | PR | Periodic | Deploy | Upgrade | Leapfrog |
|---------------------|-----|-------|---------|---------|-----------------|------------------|------|--------------|----|----------|--------|---------|----------|
| AIO                 |     |       |         |         |                 |                  |      |              |    |          |        |         |          |
| MNAIO               |     |       |         |         |                 |                  |      |              |    |          |        |         |          |
| Tempest             | x   | x     |         |         |                 |                  |      |              |    |          |        |         |          |
| Holland             | x   | x     |         |         |                 |                  |      |              |    |          |        |         |          |
| Kibana Selenium     | x   | x     |         |         |                 |                  |      |              |    |          |        |         |          |
| Horizon Selnium     |     | x     |         |         |                 |                  |      |              |    |          |        |         |          |
| MaaS Verify         |     |       |         |         |                 |                  |      |              |    |          |        |         |          |
| MaaS Verify Offline | x   | x     |         |         |                 |                  |      |              |    |          |        |         |          |
| PR                  | x   |       | x       |         | x               |                  |      | x            |    |          |        |         |          |
| Periodic            | x   | x     | x       | x       | x               | x                | x    | x            |    |          |        |         |          |
| Deploy              | x   | x     | x       |         | x               | x                |      | x            | x  |          |        |         |          |
| Upgrade             | x   |       | x       | x       | x               |                  |      | x            | x  |          |        |         |          |
| Leapfrog            | x   |       | x       |         | x               |                  |      | x            | x  |          |        |         |          |


#### Notes
* An full MaaS Verify is performed against changes to the rpc-maas repo.
* The test matrices for AIO and MNAIO jobs are defined in JJB, see the source:
  * [AIO](https://github.com/rcbops/rpc-gating/blob/master/rpc_jobs/rpc_aio.yml)
  * [MNAIO](https://github.com/rcbops/rpc-gating/blob/master/rpc_jobs/multi_node_aio.yml)
* Jenkins has a useful [categorised view](https://rpc.jenkins.cit.rackspace.net/view/AIO/), this breaks down the 90+ jobs into categories
making finding relevant jobs much easier.
* Ceph/Swift was left out of the matrix, as ceph is being phased out of RPC deployments.
* RPC Branches were left out of the matrix, as that would have caused a complexity explosion
