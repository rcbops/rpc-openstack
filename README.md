**Please use the following rules when creating rcbops MaaS plugins:**

1. Import errors result in error status
2. Inability to access a dependent service (such as keystone) also result in error status
3. Not able to obtain a client or not able to connect to the API endpoint returns status OK, and the problem is reported in the metrics as the API being down.
4. Unexpected exceptions triggered during the run cause an error status, with the text of the exception in the message.
5. Response times are reported as int32 in milliseconds. In the event of an error status, the response time metric is reported as -1.

These were ripped from @miguelgrinberg's comment in <https://github.com/rcbops/rcbops-maas/pull/43>
