#!/usr/bin/env bash
# Copyright 2017, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# (c) 2017, Jean-Philippe Evrard <jean-philippe.evrard@rackspace.co.uk>

## Shell Opts ----------------------------------------------------------------
set -e -u
set -o pipefail

# Branches lower than Newton may have ansible_host: ansible_ssh_host mapping
# that will fail because ansible_ssh_host is undefined on ansible 2.1
# Strip it.
if [[ -f /etc/openstack_deploy/user_rpcm_default_variables.yml ]]; then
    sed -i '/ansible_host/d' /etc/openstack_deploy/user_rpcm_default_variables.yml
fi
OSA_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/../../openstack-ansible && pwd)"
pushd $OSA_PATH
    if ! scripts/inventory-manage.py -g | grep ceph > /dev/null; then
        echo "No ceph found, we can continue"
    else
        echo "Ceph group found, the leapfrog can't continue"
        exit 1
    fi
popd
