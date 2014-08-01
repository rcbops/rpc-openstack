Ripped from @miguelgrinberg's comment in <https://github.com/rcbops/rcbops-maas/pull/43>

1. import errors result in error status
2. inability to access a dependent service (such as keystone) also result in error status
3. not able to obtain a client or not able to connect to the API endpoint returns status OK, and the problem is reported in the metrics as the API being down.
4. unexpected exceptions triggered during the run cause an error status, with the text of the exception in the message.
5. response times are reported as int32 in milliseconds. In the event of an error status, the response time metric is reported as -1.
