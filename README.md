**Please use the following rules when creating rcbops MaaS plugins:**

1. Import errors result in an error status.
2. Inability to access a dependent service (such as keystone) also result in an error status.
3. Not able to obtain a client or not able to connect to the API endpoint returns status OK, and the problem is reported in the metrics as the API being down.  No further metrics are sent at this point (including a response time).
4. Unexpected exceptions triggered during the run cause an error status, with the text of the exception in the message.
5. Response times are reported as uint32 in milliseconds.

A discussion of these rules can be found in <https://github.com/rcbops/rcbops-maas/pull/43>.
