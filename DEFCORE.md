# Running RefStack against RPC-OpenStack

The [RefStack](https://refstack.openstack.org/#/) tool runs a specific set of
Tempest tests against an OpenStack deployment to ensure it meets the
interoperability requirements for OpenStack clouds. This is often called
"DefCore".

You will need a fully deployed RPC environment to run the RefStack tests. AIO
environments are fine, so long as they have spare RAM and disk available for
some temporary virtual machines.  The RPC environment must have a utility
container and hardware virtualization (such as Intel VMX) must be enabled.

### Installing `refstack-client`

Within the utility container, run the following:

``` shell
git clone https://github.com/openstack/refstack-client /root/refstack-client
rm -rf ~/.pip
cd /root/refstack-client
./setup_env
```

You should now have `refstack-client` installed into a virtual environment
along with tempest in `/root/refstack-client/.venv`.

### Get the RefStack test list

The list of RefStack tests is revised regularly (every 6-8 months) and you will
need the latest list from the
[RefStack site](https://refstack.openstack.org/#/).
Go to the [DefCore Guidelines](https://refstack.openstack.org/#/guidelines) tab
and ensure the following items are selected:

* **Version:** *choose the latest available version*
* **Target Program:** OpenStack Powered Platform
* **Capability Status:** Only *Required* is checked

Be sure that the *Corresponding OpenStack Releases* contains the branch of
OpenStack that you are attempting to test.

Click **Test List** on the right side of the page and note the `wget` line
provided in the pop-up window. Run that `wget` line within `/root/refstack-
client/` directory in the utility container.

### Install tempest

From the deployment host, install tempest into the utility container:

    cd /opt/rpc-openstack/openstack-ansible/playbooks
    openstack-ansible os-tempest-install.yml

### Configure tempest

Refstack now requires pre-provisioned credentials and the corresponding
accounts file to funtion. Create an accounts file in ~/.tempest/etc/ called
accounts.yaml with the following content:

``` yaml
- username: 'admin'
  tenant_name: 'admin'
  password: 'yourpasswordhere'
  resources:
    network: 'private'
    router: 'router'
```

Next, change add the following line to the `[auth]` section in
`~/.tempest/etc/tempest.conf`:

``` conf
test_accounts_file = ~/.tempest/etc/accounts.yaml
```

Finally, in the same file, modify `use_dynamic_credentials` by setting it
to `False`:

``` conf
use_dynamic_credentials = False
```

For more information please see: https://docs.openstack.org/developer/tempest/configuration.html#pre-provisioned-credentials

### Run RefStack

Go back to the utility container and run `refstack-client`:

``` shell
cd /root/refstack-client
source .venv/bin/activate
./refstack-client test \
  -c ~/.tempest/etc/tempest.conf \
  --upload \
  --test-list 2017.01-test-list.txt \
  -v | tee -a reflog.txt
```

It will take 20-40 minutes to run, depending on the speed of your server(s).
When the run is complete, you will see a URL printed at the end of the output.
This URL contains the detailed results for your RefStack run and the results
must show 100% compliance for required tests.

As an example,
[this is our Newton (14.0) report](https://refstack.openstack.org/#/results/6a4a6cb4-13ba-42d2-8789-f456060370ca)

## Troubleshooting

If a test failed and you're not sure why, you can run that individual test
again. Use the `--regex` option provided by `ostestr` (from tempest) to specify
a regex for tests that you want to run.

Here's an example:

``` shell
cd /root/refstack-client
source .venv/bin/activate
./refstack-client test \
  -c /opt/tempest_untagged/etc/tempest.conf \
  -v \
  -- --regex 'test_list_servers_filtered_by_ip_regex'
```

Only the test(s) with `test_list_servers_filtered_by_ip_regex` in their name
will run again.  You can troubleshoot failing tests by:

* Watching `/var/log/utility/tempest.log` in the utility container shows the
  API requests that tempest is making
* Reviewing individual service logs in other containers (go look at
  neutron-server logs if a Neutron test is failing)
* Trying to reproduce the issue yourself via API or via Horizon

## Notify the OpenStack Foundation

Start by sending a formal request to the
[Interop list](mailto:interop@openstack.org). This creates a ticket with the
OpenStack Foundation to have the DefCore results updated. You can also ping
`hogepoge` in `#refstack` on Freenode to see if the process has changed.
