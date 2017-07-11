#!/usr/bin/env bash
#
# Copyright 2014-2017, Rackspace US, Inc.
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

# begin the RPC installation
cd ${RPCD_DIR}/playbooks/

# configure everything for RPC support access
run_ansible rpc-support.yml

# deploy and configure the ELK stack
if [[ "${DEPLOY_ELK}" == "yes" ]]; then
  run_ansible setup-logging.yml
fi

if [[ ! -f "${RPCM_VARIABLES}" ]]; then
  cp "${RPCD_DIR}/etc/openstack_deploy/user_rpcm_variables.yml" "${RPCM_VARIABLES}"
fi

# Download the latest release of rpc-maas
# TODO(odyssey4me):
# Remove this once rpc-gating no longer tries
# to run rpc-maas as its own thing and instead
# just uses deploy.sh end-to-end. This line
# should not be necessary as setup-maas.yml
# below includes maas-get.yml
run_ansible maas-get.yml

# deploy and configure RAX MaaS
if [[ "${DEPLOY_MAAS}" == "yes" ]]; then
  # Run the rpc-maas setup process
  run_ansible setup-maas.yml

  # verify RAX MaaS is running after all necessary
  # playbooks have been run
  run_ansible verify-maas.yml
fi
