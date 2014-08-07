**Please use the following rules when creating rcbops MaaS plugins:**

1. Import errors result in an error status.
2. Inability to access a dependent service (such as keystone) also result in an error status.
3. Not able to obtain a client or not able to connect to the API endpoint returns status OK, and the problem is reported in the metrics as the API being down.  No further metrics are sent at this point (including a response time).
4. Unexpected exceptions triggered during the run cause an error status, with the text of the exception in the message.
5. Response times are reported as uint32 in milliseconds.

A discussion of these rules can be found in <https://github.com/rcbops/rcbops-maas/pull/43>.

### LOCAL API CHECKS

***
#### nova_api_local_check.py

##### mandatory args:  
    IP address of service to test  
##### example metrics output:  

    metric nova_api_local_status uint32 1
    metric nova_api_local_response_time uint32 134.366 ms
    
***
#### cinder_api_local_check.py

##### mandatory args:
    IP address of service to test
##### example metrics output:

    metric cinder_api_local_status uint32 1
    metric cinder_api_local_response_time uint32 38.775 ms
***
#### keystone_api_local_check.py

##### mandatory args:
    IP address of service to test
##### example metrics output:

    metric keystone_api_local_status uint32 1
    metric keystone_api_local_response_time uint32 64.847 ms

***
#### neutron_api_local_check.py

##### mandatory args:
    IP address of service to test
##### example metrics output:

    metric neutron_api_local_status uint32 1
    metric neutron_api_local_response_time uint32 8.311 ms

***
#### glance_api_local_check.py

##### mandatory args:
    IP address of service to test
##### example metrics output:

    metric glance_api_local_status uint32 1
    metric glance_api_local_response_time uint32 11.663 ms

***
#### heat_api_local_check.py

##### mandatory args:
    IP address of service to test
##### example metrics output:

    metric heat_api_local_status uint32 1
    metric heat_api_local_response_time uint32 22.752 ms

***
#### service_api_local_check.py

##### mandatory args:
    <name> of service to test
    IP address of service to test
    Port of service to test
##### optional args:
    --path: path to tag on to the end of the url
    --auth: whether to authenticate with keystone before the request
    --ssl: use https or not
    --version: hit a specific version of the api

##### example metrics output:

    metric <name>_api_local_status uint32 1
    metric <name>_api_local_response_time uint32 6.222 ms

***
***

### SERVICE CHECKS

#### nova_service_check.py

##### mandatory args:
    IP address of service to test
##### example metrics output:

    metric nova-scheduler_on_host_aio1_nova_scheduler_container-e7b92e0f uint32 1
    metric nova-conductor_on_host_aio1_nova_conductor_container-dcddd54a uint32 1
    metric nova-compute_on_host_aio1_nova_compute_container-19824c74 uint32 1
    ...

***
#### cinder_service_check.py

##### mandatory args:
    IP address of service to test
##### example metrics output:

    metric cinder-scheduler_on_host_aio1_cinder_volumes_container-b6ad3de7 uint32 1
    metric cinder-volume_on_host_aio1_cinder_volumes_container-b6ad3de7 uint32 1
    ...

***
#### neutron_service_check.py

##### mandatory args:
    IP address of service to test
##### example metrics output:

    metric neutron-metadata-agent_8a1a5b16-8546-4801-a31f-e07dce8c068b_on_host_big3.localdomain uint32 1
    metric neutron-linuxbridge-agent_cac1fd39-e23d-47ea-aa20-99f0accf5584_on_host_aio1_nova_compute_container-19824c74 uint32 1
    metric neutron-dhcp-agent_d89db127-2bc7-473a-bcb0-ac89345397e0_on_host_big3.localdomain uint32 1
    metric neutron-linuxbridge-agent_e86cee43-47bf-42cd-872f-a623e458e549_on_host_big3.localdomain uint32 1
    ...

***
***
### OTHER CHECKS
***
#### glance_registry_local_check.py

##### mandatory args:
    IP address of service to test

##### example metrics output:

    metric glance_registry_local_status uint32 1
    metric glance_registry_local_response_time uint32 356.917

***
#### horizon_check.py

##### mandatory args:
    IP address of service to test
##### example metrics output:

    metric splash_status_code uint32 200
    metric splash_milliseconds double 83.557 ms
    metric login_status_code uint32 200
    metric login_milliseconds double 1344.399 ms

***
#### rabbitmq_status.py

##### optional args:
    --host: IP of service to test (default 'localhost')
    --port: port of service to test (default '15672')
    --username: username to test with (default 'guest')
    --password: password to test with (default 'guest')

##### example metrics output:

    metric disk_free_alarm int64 False
    metric uptime int64 772978111
    metric messages int64 0
    metric ack int64 532107
    metric deliver_get int64 532107
    metric deliver int64 532107
    metric fd_used int64 103
    metric publish int64 540247
    metric fd_total int64 1024
    metric mem_used int64 76674832
    metric mem_alarm int64 False
    metric mem_limit int64 1678368768
    metric sockets_total int64 829
    metric proc_used int64 1153
    metric sockets_used int64 80
    metric messages_unacknowledged int64 0
    metric messages_ready int64 0
    metric proc_total int64 1048576

***
#### galera_check.py

##### optional args:
    --host: IP of service to test (default 'localhost')
    --port: port of service to test (default '15672')

##### example metrics output:

    metric WSREP_REPLICATED_BYTES int64 320737952
    metric WSREP_RECEIVED_BYTES int64 33470
    metric WSREP_COMMIT_WINDOW double 1.000000
    metric WSREP_CLUSTER_SIZE int64 1
    metric QUERIES_PER_SECOND int64 5792715
    metric WSREP_CLUSTER_STATE_UUID string 67e41d08-165d-11e4-9d87-7e94ef43b302
    metric WSREP_CLUSTER_STATUS string Primary
    metric WSREP_LOCAL_STATE_UUID string 67e41d08-165d-11e4-9d87-7e94ef43b302
    metric WSREP_LOCAL_STATE_COMMENT string Synced
