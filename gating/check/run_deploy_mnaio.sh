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

set -eux

echo "Building a Multi Node AIO (MNAIO)"
echo "+-------------------- MNAIO ENV VARS --------------------+"
env
echo "+-------------------- MNAIO ENV VARS --------------------+"

echo "Installing python"
apt-get update && apt-get install -y python-minimal python-yaml

## Vars & Function -----------------------------------------------------------

export BASE_DIR=${BASE_DIR:-"/opt/rpc-openstack"}
source ${BASE_DIR}/scripts/functions.sh
source "$(readlink -f $(dirname ${0}))/../gating_vars.sh"
source "$(readlink -f $(dirname ${0}))/../mnaio_vars.sh"

## Main --------------------------------------------------------------------

# If there is no set of images available yet, or this is the deploy
# action, then we need to build from scratch.
# We need to run the OSA deploy playbook for some pre-configuration
# before doing the RPC-O bits. The conditional was already evaluated in
# mnaio_vars, so we key off DEPLOY_VMS here.
if [[ "${DEPLOY_VMS}" == "true" ]]; then
  # apply various modifications for mnaio
  pushd /opt/openstack-ansible-ops/multi-node-aio
    # By default the MNAIO deploys metering services, so we override
    # osa_enable_meter to prevent those services from being deployed.
    # TODO(odyssey4me):
    # Remove this once https://review.openstack.org/604034 has merged.
    sed -i 's/osa_enable_meter: true/osa_enable_meter: false/' playbooks/group_vars/all.yml

    export DEPLOY_OSA="true"
    export PRE_CONFIG_OSA="true"

    # Run the initial deployment configuration
    run_mnaio_playbook playbooks/deploy-osa.yml
  popd
else
  # If this is not a deploy test, and the images were used in
  # the 'pre' stage to setup the VM's, then we do not need to
  # execute any more of this script.
  # We implement a simple 5 minute wait to give time for the
  # containers to start in the VM's.
  echo "MNAIO RPC-O deploy completed using images... waiting 5 mins for system startup."
  sleep 300
  exit 0
fi

# set OSA branch
pushd /opt/rpc-openstack
  OSA_COMMIT=`git submodule status openstack-ansible | egrep --only-matching '[a-f0-9]{40}'`
  export OSA_BRANCH=${OSA_COMMIT}
popd

echo "Multi Node AIO setup completed..."

# capture all RE_ variables for push to infra1
> /opt/rpc-openstack/RE_ENV
env | grep RE_ | while read -r match; do
  varName=$(echo ${match} | cut -d= -f1)
  echo "export ${varName}='${!varName}'" >> /opt/rpc-openstack/RE_ENV
done

# check if we're using artifacts or not
if [[ ${RE_JOB_IMAGE} =~ no_artifacts$ ]]; then
  export RPC_APT_ARTIFACT_ENABLED=no
  echo "export RPC_APT_ARTIFACT_ENABLED=no" >> /opt/rpc-openstack/RE_ENV
  ${MNAIO_SSH} "apt-get -qq update; DEBIAN_FRONTEND=noninteractive apt-get -y dist-upgrade"
elif [[ ${RE_JOB_IMAGE} =~ loose_artifacts$ ]]; then
  # Set the apt artifact mode
  export RPC_APT_ARTIFACT_MODE=loose
  echo "export RPC_APT_ARTIFACT_MODE=loose" >> /opt/rpc-openstack/RE_ENV
  ${MNAIO_SSH} "apt-get -qq update; DEBIAN_FRONTEND=noninteractive apt-get -y dist-upgrade"
fi

# Set the appropriate scenario variables
if [[ "${RE_JOB_SCENARIO}" == "ceph" ]]; then
  echo "export DEPLOY_CEPH=yes" >> /opt/rpc-openstack/RE_ENV
  echo "export DEPLOY_SWIFT=no" >> /opt/rpc-openstack/RE_ENV
elif [[ "${RE_JOB_SCENARIO}" == "ironic" ]]; then
  echo "export DEPLOY_IRONIC=yes" >> /opt/rpc-openstack/RE_ENV
fi

# prepare rpc-o configs
set -xe
echo "+---------------- MNAIO RELEASE AND KERNEL --------------+"
lsb_release -a
uname -a
echo "+---------------- MNAIO RELEASE AND KERNEL --------------+"
scp -r -o StrictHostKeyChecking=no /opt/rpc-openstack root@infra1:/opt/
${MNAIO_SSH} <<EOC
  set -xe
  echo "+--------------- INFRA1 RELEASE AND KERNEL --------------+"
  lsb_release -a
  uname -a
  echo "+--------------- INFRA1 RELEASE AND KERNEL --------------+"
  cp /etc/openstack_deploy/user_variables.yml /etc/openstack_deploy/user_variables.yml.bak
  cp -R /opt/rpc-openstack/openstack-ansible/etc/openstack_deploy /etc
  cp /etc/openstack_deploy/user_variables.yml.bak /etc/openstack_deploy/user_variables.yml
  cp /opt/rpc-openstack/rpcd/etc/openstack_deploy/user_*.yml /etc/openstack_deploy
  cp /opt/rpc-openstack/rpcd/etc/openstack_deploy/env.d/* /etc/openstack_deploy/env.d
EOC

# start the rpc-o install from infra1
${MNAIO_SSH} "source /opt/rpc-openstack/RE_ENV; \
              pushd /opt/rpc-openstack; \
              export DEPLOY_ELK=yes; \
              export DEPLOY_MAAS=no; \
              export DEPLOY_TELEGRAF=no; \
              export DEPLOY_INFLUX=no; \
              export DEPLOY_AIO=no; \
              export DEPLOY_HAPROXY=yes; \
              export DEPLOY_OA=yes; \
              export DEPLOY_TEMPEST=no; \
              export DEPLOY_CEILOMETER=no; \
              export DEPLOY_RPC=yes; \
              export ANSIBLE_FORCE_COLOR=true; \
              scripts/deploy.sh"

echo "MNAIO RPC-O deploy completed..."
