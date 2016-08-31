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
    --overrides /etc/openstack_deploy/user_extras_variables.yml \
    --output-file /etc/openstack_deploy/user_rpco_variables_overrides.yml
"${BASE_DIR}"/scripts/migrate-yaml.py --for-testing-take-new-vars-only \
  --defaults "${RPCD_DIR}"/etc/openstack_deploy/user_osa_variables_defaults.yml \
  --overrides /etc/openstack_deploy/user_variables.yml \
  --output-file /etc/openstack_deploy/user_osa_variables_overrides.yml
cp -a ${RPCD_DIR}/etc/openstack_deploy/*defaults* /etc/openstack_deploy
rm /etc/openstack_deploy/user_extras_variables.yml /etc/openstack_deploy/user_variables.yml

# TASK #1
# Bug: https://github.com/rcbops/rpc-openstack/issues/1345
# Issue: horizon-extensions now gets pulled from a different location; the
#        git cache on the repo_all containers needs to be deleted so we can
#        grab the new repo.  Failing to do this will cause repo-install.yml
#        to fail to run.
cd ${RPCD_DIR}/playbooks
ansible -m file -a "path=/var/www/repo/openstackgit/horizon-extensions state=absent" repo_all
