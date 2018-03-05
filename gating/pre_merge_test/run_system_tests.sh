#!/bin/bash

## Deploy virualenv for testing enironment molecule/ansible-playbook/infratest

## Shell Opts ----------------------------------------------------------------

set -ev
set -o pipefail

## Variables -----------------------------------------------------------------

RE_HOOK_ARTIFACT_DIR="${RE_HOOK_ARTIFACT_DIR:-/tmp/artifacts}"
export RE_HOOK_RESULT_DIR="${RE_HOOK_RESULT_DIR:-/tmp/results}"
SYS_WORKING_DIR=$(mktemp  -d -t system_test_workingdir.XXXXXXXX)
export SYS_VENV_NAME="${SYS_VENV_NAME:-venv-molecule}"
SYS_TEST_SOURCE_BASE="${SYS_TEST_SOURCE_BASE:-https://github.com/rcbops}"
SYS_TEST_SOURCE="${SYS_TEST_SOURCE:-rpc-openstack-system-tests}"
SYS_TEST_SOURCE_REPO="${SYS_TEST_SOURCE_BASE}/${SYS_TEST_SOURCE}"
SYS_TEST_BRANCH="${SYS_TEST_BRANCH:-master}"
export SYS_INVENTORY="/opt/openstack-ansible/playbooks/inventory"

## Main ----------------------------------------------------------------------


# 1. Clone test repo into working directory.
pushd "${SYS_WORKING_DIR}"
git clone "${SYS_TEST_SOURCE_REPO}"
pushd "${SYS_TEST_SOURCE}"

# Checkout defined branch
git checkout "${SYS_TEST_BRANCH}"

# Gather submodules
git submodule init
git submodule update --recursive


# 2. Execute script from repo
./execute_tests.sh

# 3. Collect results from script
tar -xf test_results.tar -C "${RE_HOOK_RESULT_DIR}"

# 4. Collect logs from script
# Molecule does not produce logs outside of STDOUT
popd
