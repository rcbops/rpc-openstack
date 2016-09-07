#!/usr/bin/env bash
# Copyright 2014-2016, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# (c) 2015, Nolan Brubaker <nolan.brubaker@rackspace.com>
# (c) 2016, Matthew Thode <matt.thode@rackspace.com>

set -eux -o pipefail

BASE_DIR=$( cd "$( dirname ${0} )" && cd ../ && pwd )
OA_DIR="$BASE_DIR/openstack-ansible"
RPCD_DIR="$BASE_DIR/rpcd"

# TASK #0
# Bug: https://github.com/rcbops/u-suk-dev/issues/347
# Issue: Variables files have been reorganized, run a migration script to move
#        them to the new location.
"${BASE_DIR}"/scripts/migrate-yaml.py --for-testing-take-new-vars-only \
    --defaults "${RPCD_DIR}"/etc/openstack_deploy/user_rpco_variables_defaults.yml \
    --overrides /etc/openstack_deploy/user_extra_variables.yml \
    --output-file /etc/openstack_deploy/user_rpco_variables_overrides.yml
"${BASE_DIR}"/scripts/migrate-yaml.py --for-testing-take-new-vars-only \
  --defaults "${RPCD_DUR}"/etc/openstack_deploy/user_osa_variables_defaults.yml \
  --overrides /etc/openstack_deploy/user_variables.yml \
  --output-file /etc/openstack_deploy/user_osa_variables_overrides.yml
rm /etc/openstack_deploy/user_extra_variables.yml /etc/openstack_deploy/user_variables.yml

# TASK #1
# Bug: https://github.com/rcbops/u-suk-dev/issues/293
# Issue: We need to analyze support's maintenance plan to determine which
# pieces we can orchestrate with ansible. This should be added to a
# pre-upgrade task list.
cd ${RPCD_DIR}/playbooks
openstack-ansible rpc-pre-upgrades.yml

# TASK #2
# Bug: https://github.com/rcbops/u-suk-dev/issues/199
# Issue: To avoid any dependency issues that have occured in the past, the
#        repo_server containers are re-built. This was done as part of the
#        OSA upgrade script in liberty, but is not done in the OSA mitaka
#        upgrade script. Thus, we destroy the containers here.
cd ${OA_DIR}/playbooks
openstack-ansible lxc-containers-destroy.yml --limit repo_all
openstack-ansible setup-hosts.yml --limit repo_all

# TASK #3
# https://github.com/rcbops/u-suk-dev/issues/392
# Upgrade openstack-ansible
pushd ${OA_DIR}
export I_REALLY_KNOW_WHAT_I_AM_DOING=true
echo "YES" | ${OA_DIR}/scripts/run-upgrade.sh
popd

# TASK #4 TODO: This task should be moved somewhere towards the bottom once
#               we get a more robust script going.
# Bug: https://github.com/rcbops/u-suk-dev/issues/366
# Description: Run post-upgrade tasks.
#              For a detailed description, please see the README in
#              the rpc_post_upgrade role directory.
cd ${RPCD_DIR}/playbooks
openstack-ansible rpc-post-upgrades.yml
