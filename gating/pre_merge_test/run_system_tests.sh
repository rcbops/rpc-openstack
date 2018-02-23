#!/bin/bash

## Deploy virualenv for testing enironment molecule/ansible-playbook/infratest

## Shell Opts ----------------------------------------------------------------

set -ev
set -o pipefail
export ANSIBLE_HOST_KEY_CHECKING=False

## Variables -----------------------------------------------------------------

SYS_WORKING_DIR=$(mktemp  -d -t system_test_workingdir.XXXXXXXX)
SYS_VENV_NAME="${SYS_VENV_NAME:-venv-molecule}"
SYS_TEST_SOURCE_BASE="${SYS_TEST_SOURCE_BASE:-https://github.com/rcbops}"
SYS_TEST_SOURCE="${SYS_TEST_SOURCE:-rpc-openstack-system-tests}"
SYS_TEST_SOURCE_REPO="${SYS_TEST_SOURCE_BASE}/${SYS_TEST_SOURCE}"
SYS_TEST_BRANCH="${SYS_TEST_BRANCH:-master}"
SYS_CONSTRAINTS="${SYS_WORKING_DIR}/${SYS_TEST_SOURCE}/constraints.txt"
SYS_REQUIREMENTS="${SYS_WORKING_DIR}/${SYS_TEST_SOURCE}/requirements.txt"
SYS_INVENTORY="/opt/openstack-ansible/playbooks/inventory"

## Main ----------------------------------------------------------------------

# Clone test repository into working directory.
pushd ${SYS_WORKING_DIR}

git clone ${SYS_TEST_SOURCE_REPO}

pushd ${SYS_TEST_SOURCE}
# Checkout defined branch
git checkout ${SYS_TEST_BRANCH}

# Gather submodules
git submodule init
git submodule update --recursive
popd


# Create virtualenv for molecule
virtualenv --no-pip --no-setuptools --no-wheel ${SYS_VENV_NAME}

# Activate virtualenv
source ${SYS_VENV_NAME}/bin/activate

# Ensure that correct pip version is installed
PIP_TARGET="$(awk -F= '/^pip==/ {print $3}' ${SYS_CONSTRAINTS})"
VENV_PYTHON="${SYS_VENV_NAME}/bin/python"
VENV_PIP="${SYS_VENV_NAME}/bin/pip"

if [[ "$(${VENV_PIP} --version)" != "pip ${PIP_TARGET}"* ]]; then
    CURL_CMD="curl --silent --show-error --retry 5"
    OUTPUT_FILE="get-pip.py"
    ${CURL_CMD} https://bootstrap.pypa.io/get-pip.py > ${OUTPUT_FILE}  \
        || ${CURL_CMD} https://raw.githubusercontent.com/pypa/get-pip/master/get-pip.py > ${OUTPUT_FILE}
    GETPIP_OPTIONS="pip setuptools wheel --constraint ${SYS_CONSTRAINTS}"
    ${VENV_PYTHON} ${OUTPUT_FILE} ${GETPIP_OPTIONS} \
        || ${VENV_PYTHON} ${OUTPUT_FILE} --isolated ${GETPIP_OPTIONS}
fi

# Install test suite requirements
PIP_OPTIONS="-c ${SYS_CONSTRAINTS} -r ${SYS_REQUIREMENTS}"
${VENV_PIP} install ${PIP_OPTIONS} || ${VENV_PIP} install --isolated ${PIP_OPTIONS}

# Generate moleculerized inventory from openstack-ansible dynamic inventory
${SYS_INVENTORY}/dynamic_inventory.py > ${SYS_WORKING_DIR}/dynamic_inventory.json

pushd ${SYS_TEST_SOURCE}

# Run molecule converge and verify
# for each submodule in ${SYS_TEST_SOURCE}/molecules
set +e # allow test stages to return errors
for TEST in $(ls molecules) ; do
    ./moleculerize.py --output molecules/$TEST/molecule/default/molecule.yml /tmp/dynamic_inventory.json
    pushd molecules/$TEST
    molecule converge
    molecule verify
    popd
done

popd

popd
