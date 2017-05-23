#!/usr/bin/env bash
# Copyright 2014-2017 , Rackspace US, Inc.
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

## Vars ----------------------------------------------------------------------

# To provide flexibility in the jobs, we have the ability to set any
# parameters that will be supplied on the ansible-playbook CLI.
export ANSIBLE_PARAMETERS=${ANSIBLE_PARAMETERS:--v}

# Set this to YES if you want to replace any existing artifacts for the current
# release with those built in this job.
export REPLACE_ARTIFACTS=${REPLACE_ARTIFACTS:-no}

# Set this to YES if you want to push any changes made in this job to rpc-repo.
export PUSH_TO_MIRROR=${PUSH_TO_MIRROR:-no}

# The BASE_DIR needs to be set to ensure that the scripts
# know it and use this checkout appropriately.
export BASE_DIR=${PWD}

# We want the role downloads to be done via git
# This ensures that there is no race condition with the artifacts-git job
export ANSIBLE_ROLE_FETCH_MODE="git-clone"

## Main ----------------------------------------------------------------------

# The derive-artifact-version.sh script expects the git clone to
# be at /opt/rpc-openstack, so we link the current folder there.
ln -sfn ${PWD} /opt/rpc-openstack

# bootstrap Ansible and the AIO config
cd /opt/rpc-openstack
./scripts/bootstrap-ansible.sh
./scripts/bootstrap-aio.sh

# Now use GROUP_VARS of OSA and RPC
sed -i "s|GROUP_VARS_PATH=.*|GROUP_VARS_PATH=\"\${GROUP_VARS_PATH:-${BASE_DIR}/openstack-ansible/playbooks/inventory/group_vars/:${BASE_DIR}/group_vars/:/etc/openstack_deploy/group_vars/}\"|" /usr/local/bin/openstack-ansible.rc
sed -i "s|HOST_VARS_PATH=.*|HOST_VARS_PATH=\"\${HOST_VARS_PATH:-${BASE_DIR}/openstack-ansible/playbooks/inventory/host_vars/:${BASE_DIR}/host_vars/:/etc/openstack_deploy/host_vars/}\"|" /usr/local/bin/openstack-ansible.rc

# Figure out the release version
export RPC_RELEASE="$(/opt/rpc-openstack/scripts/artifacts-building/derive-artifact-version.sh)"

# Remove the env.d configurations that set the build to use
# container artifacts. We don't want this because container
# artifacts are built using python artifacts.
sed -i.bak '/lxc_container_variant: /d' /etc/openstack_deploy/env.d/*.yml

# Remove the RPC-O default configurations that are necessary
# for deployment, but cause the build to break due to the fact
# that they require the container artifacts to be available,
# but those are not yet built.
sed -i.bak '/lxc_image_cache_server: /d' /etc/openstack_deploy/user_osa_variables_defaults.yml
sed -i.bak '/lxc_cache_default_variant: /d' /etc/openstack_deploy/user_osa_variables_defaults.yml
sed -i.bak '/lxc_cache_download_template_extra_options: /d' /etc/openstack_deploy/user_osa_variables_defaults.yml
sed -i.bak '/lxc_container_variant: /d' /etc/openstack_deploy/user_osa_variables_defaults.yml
sed -i.bak '/lxc_container_download_template_extra_options: /d' /etc/openstack_deploy/user_osa_variables_defaults.yml

# Set override vars for the artifact build
echo "rpc_release: ${RPC_RELEASE}" >> /etc/openstack_deploy/user_rpco_variables_overrides.yml
echo "repo_build_wheel_selective: no" >> /etc/openstack_deploy/user_osa_variables_overrides.yml
echo "repo_build_venv_selective: no" >> /etc/openstack_deploy/user_osa_variables_overrides.yml
cp scripts/artifacts-building/user_rcbops_artifacts_building.yml /etc/openstack_deploy/

# Prepare to run the playbooks
cd /opt/rpc-openstack/openstack-ansible/playbooks

# The host must only have the base Ubuntu repository configured.
# All updates (security and otherwise) must come from the RPC-O apt artifacting.
# This is also being done to ensure that the python artifacts are built using
# the same sources as the container artifacts will use.
openstack-ansible /opt/rpc-openstack/rpcd/playbooks/configure-apt-sources.yml \
                  -e "host_ubuntu_repo=http://mirror.rackspace.com/ubuntu" \
                  ${ANSIBLE_PARAMETERS}

# Setup the repo container and build the artifacts
openstack-ansible setup-hosts.yml \
                  -e container_group=repo_all \
                  ${ANSIBLE_PARAMETERS}

openstack-ansible repo-install.yml \
                  ${ANSIBLE_PARAMETERS}


# Read the OS information
source /etc/os-release
ARCH=$(uname -p)

# If there are artifacts for this release, then set PUSH_TO_MIRROR to NO
if curl http://rpc-repo.rackspace.com/os-releases/${RPC_RELEASE}/${ID}-${VERSION_ID}-${ARCH}/MANIFEST.in; then
  export PUSH_TO_MIRROR="NO"
fi

# If REPLACE_ARTIFACTS is YES then set PUSH_TO_MIRROR to YES
if [[ "$(echo ${REPLACE_ARTIFACTS} | tr [a-z] [A-Z])" == "YES" ]]; then
  export PUSH_TO_MIRROR="YES"
fi

if [[ "$(echo ${PUSH_TO_MIRROR} | tr [a-z] [A-Z])" == "YES" ]]; then
  if [ -z ${REPO_USER_KEY+x} ] || [ -z ${REPO_USER+x} ] || [ -z ${REPO_HOST+x} ] || [ -z ${REPO_HOST_PUBKEY+x} ]; then
    echo "Skipping upload to rpc-repo as the REPO_* env vars are not set."
    exit 1
  else
    # Prep the ssh key for uploading to rpc-repo
    mkdir -p ~/.ssh/
    set +x
    REPO_KEYFILE=~/.ssh/repo.key
    cat $REPO_USER_KEY > ${REPO_KEYFILE}
    chmod 600 ${REPO_KEYFILE}
    set -x

    # Ensure that the repo server public key is a known host
    grep "${REPO_HOST}" ~/.ssh/known_hosts || echo "${REPO_HOST} $(cat $REPO_HOST_PUBKEY)" >> ~/.ssh/known_hosts

    # Create the Ansible inventory for the upload
    echo '[mirrors]' > /opt/inventory
    echo "repo ansible_host=${REPO_HOST} ansible_user=${REPO_USER} ansible_ssh_private_key_file='${REPO_KEYFILE}' " >> /opt/inventory

    # Upload the artifacts to rpc-repo
    REPO_CONTAINER_NAME=$(lxc-ls -1 '.*_repo_' | head -n1)
    REPO_RELEASE_NAME=$(ls -1 /openstack/${REPO_CONTAINER_NAME}/repo/os-releases/*/ | head -n1)
    openstack-ansible -i /opt/inventory \
                      /opt/rpc-openstack/scripts/artifacts-building/python/upload-python-artifacts.yml \
                      -e repo_container_name=${REPO_CONTAINER_NAME} \
                      -e repo_release_name=${REPO_RELEASE_NAME} \
                      ${ANSIBLE_PARAMETERS}
  fi
else
  echo "Skipping upload to rpc-repo as the PUSH_TO_MIRROR env var is not set to 'YES'."
fi
