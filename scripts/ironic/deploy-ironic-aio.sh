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

## Shell Opts ----------------------------------------------------------------

set -e -u -x
set -o pipefail

## Functions -----------------------------------------------------------------

export BASE_DIR=${BASE_DIR:-"/opt/rpc-openstack"}
source ${BASE_DIR}/scripts/functions.sh

## Main ----------------------------------------------------------------------

# Check the openstack-ansible submodule status
check_submodule_status

# Ansible and AIO setup
DEPLOY_IRONIC="yes" DEPLOY_AIO="yes" DEPLOY_RPC="no" DEPLOY_OA="no" ${BASE_DIR}/scripts/deploy.sh
# Pre-deployment configuration for ironic
openstack-ansible ${BASE_DIR}/scripts/ironic/playbooks/ironic-pre-config.yml
# Deploy RPC
${BASE_DIR}/scripts/deploy.sh
# Post-deployment configuration for ironic
openstack-ansible ${BASE_DIR}/scripts/ironic/playbooks/ironic-post-install-config.yml
# Re-run ironic installation to include the post-config
openstack-ansible ${OA_DIR}/playbooks/os-ironic-install.yml
