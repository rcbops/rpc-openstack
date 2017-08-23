=======================
Post Upgrade Procedures
=======================

An Ansible role that runs operational post-upgrade procedures.

These procedures include:

* Verify ``wsrep_cluster_size`` is equal to the number of Galera hosts in inventory.

* Verify ``wsrep_cluster_status`` for all Galera hosts is ``Primary``.

* Verify the RabbitMQ cluster does not have `network partitions <https://www.rabbitmq.com/partitions.html>`_.

* Verify Nova, Cinder, and Neutron services are reporting in the ``up`` or ``:-)`` status.

* Verify the md5sums of the Swift rings and configuration files have no errors.

* Verify Elasticsearch indexes are reporting ``green`` as their health.

.. note:
  
  This role is intentionally littered with debug tasks. This is to help the operator
  with any questions they may have about the values being checked.

Adding tasks to this role
~~~~~~~~~~~~~~~~~~~~~~~~

If at any point you would like to see a task added to this role, please submit an issue to
rpc-openstack explaining what you would like to add, and why. Issues can be submitted
`here <https://github.com/rcbops/rpc-openstack/issues>`_.
