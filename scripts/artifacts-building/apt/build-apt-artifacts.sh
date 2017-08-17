#!/usr/bin/env bash
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

set -e
set -o pipefail

## Vars ----------------------------------------------------------------------

# To provide flexibility in the jobs, we have the ability to set any
# parameters that will be supplied on the ansible-playbook CLI.
export ANSIBLE_PARAMETERS=${ANSIBLE_PARAMETERS:--v}

# Set this to NO if you do not want to pull any existing data from rpc-repo.
export PULL_FROM_MIRROR=${PULL_FROM_MIRROR:-yes}

# Set this to YES if you want to replace any existing artifacts for the current
# release with those built in this job.
export RECREATE_SNAPSHOTS=${REPLACE_ARTIFACTS:-no}

# Set this to YES if you want to push any changes made in this job to rpc-repo.
export PUSH_TO_MIRROR=${PUSH_TO_MIRROR:-no}

# The BASE_DIR needs to be set to ensure that the scripts
# know it and use this checkout appropriately.
export BASE_DIR=${PWD}

# We want the role downloads to be done via git
# This ensures that there is no race condition with the artifacts-git job
export ANSIBLE_ROLE_FETCH_MODE="git-clone"

# These are allowed to be flexible for the purpose of testing by hand.
export PUBLISH_SNAPSHOT=${PUBLISH_SNAPSHOT:-yes}
export RPC_ARTIFACTS_FOLDER=${RPC_ARTIFACTS_FOLDER:-/var/www/artifacts}
export RPC_ARTIFACTS_PUBLIC_FOLDER=${RPC_ARTIFACTS_PUBLIC_FOLDER:-/var/www/repo}

# We do not want to rewrite the host apt sources when executing bootstrap-ansible
export HOST_SOURCES_REWRITE="no"


## Main ----------------------------------------------------------------------

if [ -z ${REPO_USER_KEY+x} ] || [ -z ${REPO_USER+x} ] || [ -z ${REPO_HOST+x} ] || [ -z ${REPO_HOST_PUBKEY+x} ]; then
  echo "ERROR: The required REPO_ environment variables are not set."
  exit 1
elif [ -z ${GPG_PRIVATE+x} ] || [ -z ${GPG_PUBLIC+x} ]; then
  echo "ERROR: The required GPG_ environment variables are not set."
  exit 1
fi

# The derive-artifact-version.sh script expects the git clone to
# be at /opt/rpc-openstack, so we link the current folder there.
if [[ "${PWD}" != "/opt/rpc-openstack" ]]; then
  ln -sfn ${PWD} /opt/rpc-openstack
fi

# Remove any previous installed plugins, libraries,
# facts and ansible/openstack-ansible refs. This
# ensures that as we upgrade/downgrade on the long
# running jenkins slave we do not get interference
# from previously installed/configured items.
rm -rf /etc/ansible /etc/openstack_deploy /usr/local/bin/ansible* /usr/local/bin/openstack-ansible*

# Install Ansible
./scripts/bootstrap-ansible.sh
cp scripts/artifacts-building/apt/lookup/* /etc/ansible/roles/plugins/lookup/

# Ensure the required folders are present
mkdir -p ${RPC_ARTIFACTS_FOLDER}
mkdir -p ${RPC_ARTIFACTS_PUBLIC_FOLDER}

set +x
# Setup the repo key for package download/upload
REPO_KEYFILE=~/.ssh/repo.key
cat $REPO_USER_KEY > ${REPO_KEYFILE}
chmod 600 ${REPO_KEYFILE}

# Setup the GPG key for package signing
cat $GPG_PRIVATE > ${RPC_ARTIFACTS_FOLDER}/aptly.private.key
cat $GPG_PUBLIC > ${RPC_ARTIFACTS_FOLDER}/aptly.public.key
set -x

# Ensure that the repo server public key is a known host
grep "${REPO_HOST}" ~/.ssh/known_hosts || echo "${REPO_HOST} $(cat $REPO_HOST_PUBKEY)" >> ~/.ssh/known_hosts

# Create an inventory to use
echo '[all]' > /opt/inventory
echo "localhost ansible_python_interpreter='/usr/bin/python2'" >> /opt/inventory
echo '[mirrors]' >> /opt/inventory
echo "repo ansible_host=${REPO_HOST} ansible_user=${REPO_USER} ansible_ssh_private_key_file='${REPO_KEYFILE}' " >> /opt/inventory

# Remove the previously used rpc-repo.log file to prevent
# it growing too large. We want a fresh log for every job.
[ -e /var/log/rpc-repo.log ] && rm -f /var/log/rpc-repo.log

# Execute the playbooks
cd ${BASE_DIR}/scripts/artifacts-building/apt
ansible-playbook -i /opt/inventory ${ANSIBLE_PARAMETERS} aptly-pre-install.yml
ansible-playbook -i /opt/inventory ${ANSIBLE_PARAMETERS} aptly-all.yml

source /opt/rpc-openstack/openstack-ansible/scripts/openstack-ansible.rc
ansible-playbook -i /opt/inventory ${ANSIBLE_PARAMETERS} apt-artifacts-testing.yml
