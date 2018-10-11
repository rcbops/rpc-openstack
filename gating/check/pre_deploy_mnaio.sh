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

set -exu

echo "Preparing a Multi Node AIO (MNAIO)"

## Vars and Functions --------------------------------------------------------

source "$(readlink -f $(dirname ${0}))/../gating_vars.sh"

source /opt/rpc-openstack/scripts/functions.sh

source "$(readlink -f $(dirname ${0}))/../mnaio_vars.sh"

## Main ----------------------------------------------------------------------

# Save a backup of the original file
if [[ ! -e /etc/apt/sources.list.original ]]; then
  mv /etc/apt/sources.list /etc/apt/sources.list.original
fi

# Set the environment variables
DISTRO_MIRROR="http://mirror.rackspace.com/ubuntu"
DISTRO_COMPONENTS="main,universe"

# Get the distribution name
if [[ -e /etc/lsb-release ]]; then
  source /etc/lsb-release
  DISTRO_RELEASE=${DISTRIB_CODENAME}
elif [[ -e /etc/os-release ]]; then
  source /etc/os-release
  DISTRO_RELEASE=${UBUNTU_CODENAME}
else
  echo "Unable to determine distribution due to missing lsb/os-release files."
  exit 1
fi

# Rewrite the apt sources file
cat << EOF >/etc/apt/sources.list
deb ${DISTRO_MIRROR} ${DISTRO_RELEASE} ${DISTRO_COMPONENTS//,/ }
deb ${DISTRO_MIRROR} ${DISTRO_RELEASE}-updates ${DISTRO_COMPONENTS//,/ }
deb ${DISTRO_MIRROR} ${DISTRO_RELEASE}-backports ${DISTRO_COMPONENTS//,/ }
deb ${DISTRO_MIRROR} ${DISTRO_RELEASE}-security ${DISTRO_COMPONENTS//,/ }
EOF

# Add apt debug configuration
echo 'Debug::Acquire::http "true";' > /etc/apt/apt.conf.d/99debug

# Ensure package installs are in headless mode
export DEBIAN_FRONTEND=noninteractive

# Update the apt cache
apt-get update

# Install pre-requisites
pkgs_to_install=""
dpkg-query --list | grep python-minimal &>/dev/null || pkgs_to_install+="python-minimal "
dpkg-query --list | grep python-yaml &>/dev/null || pkgs_to_install+="python-yaml "
dpkg-query --list | grep curl &>/dev/null || pkgs_to_install+="curl "
if [ "${pkgs_to_install}" != "" ]; then
  apt-get install -y ${pkgs_to_install}
fi

# checkout openstack-ansible-ops
if [ ! -d "/opt/openstack-ansible-ops" ]; then
  git clone --recursive https://github.com/openstack/openstack-ansible-ops /opt/openstack-ansible-ops
else
  pushd /opt/openstack-ansible-ops
    git fetch --all
  popd
fi

# build the multi node aio
pushd /opt/openstack-ansible-ops/multi-node-aio
  # Prepare the multi node aio host
  # Note (odyssey4me):
  # We cannot use build.sh here because the playbook imports
  # result in running all plays with all tasks having a conditional
  # set on them, and because the VM's aren't running at this stage
  # the plays fail. This is a workaround until there are upstream
  # improvements to counteract that issue.
  source bootstrap.sh
  source ansible-env.rc
  [[ "${SETUP_HOST}" == "true" ]] && run_mnaio_playbook playbooks/setup-host.yml
  [[ "${SETUP_PXEBOOT}" == "true" ]] && run_mnaio_playbook playbooks/deploy-acng.yml
  [[ "${SETUP_PXEBOOT}" == "true" ]] && run_mnaio_playbook playbooks/deploy-pxe.yml
  [[ "${SETUP_DHCPD}" == "true" ]] && run_mnaio_playbook playbooks/deploy-dhcp.yml
  [[ "${DEPLOY_VMS}" == "true" ]] && run_mnaio_playbook playbooks/deploy-vms.yml

  # If there are images available, and this is not the 'deploy' action,
  # then we need to download the images, then create the VM's. The conditional
  # was already evaluated in mnaio_vars, so we key off DEPLOY_VMS here.
  if [[ "${DEPLOY_VMS}" == "false" ]]; then
    run_mnaio_playbook playbooks/download-vms.yml -e manifest_url=${RPCO_IMAGE_MANIFEST_URL} -e aria2c_log_path=${RE_HOOK_ARTIFACT_DIR}
    run_mnaio_playbook playbooks/deploy-vms.yml
  fi
popd

echo "Multi Node AIO preparation completed..."
