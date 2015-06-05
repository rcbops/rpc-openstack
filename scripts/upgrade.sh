#!/usr/bin/env bash
# Copyright 2014, Rackspace US, Inc.
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
set -eux pipefail

OSAD_DIR='/opt/rpc-openstack/os-ansible-deployment'
RPCD_DIR='/opt/rpc-openstack/rpcd'

# Do the upgrade for os-ansible-deployment components
cd ${OSAD_DIR}
${OSAD_DIR}/scripts/run-upgrade.sh

# Prevent the deployment script from re-running the OSAD playbooks
export DEPLOY_OSAD="no"

# Do the upgrade for the RPC components
source ${OSAD_DIR}/scripts/scripts-library.sh
cd ${RPCD_DIR}
${RPCD_DIR}/scripts/deploy.sh
