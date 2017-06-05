#!/usr/bin/env bash

set -e -u -x
set -o pipefail

source ${BASE_DIR}/scripts/functions.sh

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

# Get MaaS: This will always run which will get the latest code but do
# nothing with it unless setup-maas.yml is run.
run_ansible maas-get.yml

# deploy and configure RAX MaaS
if [[ "${DEPLOY_MAAS}" == "yes" ]]; then
  # Run the rpc-maas setup process
  run_ansible setup-maas.yml

  # verify RAX MaaS is running after all necessary
  # playbooks have been run
  run_ansible verify-maas.yml
fi
