#!/bin/bash

## Shell Opts ----------------------------------------------------------------

set -euv
set -o pipefail

## Vars ----------------------------------------------------------------------

export DEPLOY_AIO="true"

if [[ ${RE_JOB_IMAGE} =~ no_artifacts$ ]]; then
  # Set the env var to disable artifact usage
  export RPC_APT_ARTIFACT_ENABLED="no"

  # Upgrade to the absolute latest
  # available packages.
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get -y dist-upgrade

elif [[ ${RE_JOB_IMAGE} =~ loose_artifacts$ ]]; then
  # Set the apt artifact mode
  export RPC_APT_ARTIFACT_MODE="loose"
  export RPC_APT_ARTIFACT_ENABLED="yes"

  # Upgrade to the absolute latest
  # available packages.
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get -y dist-upgrade

elif [[ ${RE_JOB_IMAGE} =~ strict_artifacts$ ]]; then
  # Set the apt artifact mode
  export RPC_APT_ARTIFACT_MODE="strict"
  export RPC_APT_ARTIFACT_ENABLED="yes"
fi

# In order to get the value for rpc_release, we need to use
# a python script, so we need to make sure that python and
# the python yaml library are installed. If not, the value
# for rpc_release cannot be read and the check for the value
# will result in a null return, causing all artifacts to be
# disabled.
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y python-minimal python-yaml

# When a PR contains a change to rpc_release, there may not
# be any artifacts for the new release version. If this is
# the case then we need to disable the artifact usage. In
# order to figure out whether there are artifacts available,
# we need to source the functions so that we have the right
# variables available to use.
source $(dirname ${0})/../../scripts/functions.sh

# Check for available artifacts and disable artifact usage
# if they are not available.
CHECK_URL="${HOST_RCBOPS_REPO}/apt-mirror/integrated/dists/${RPC_RELEASE}-${DISTRIB_CODENAME}"
if ! curl --output /dev/null --silent --head --fail ${CHECK_URL}; then
  export RPC_APT_ARTIFACT_ENABLED="no"
fi

## Functions -----------------------------------------------------------------

## Main ----------------------------------------------------------------------

# Run the deployment script
bash -c "$(readlink -f $(dirname ${0})/../../scripts/deploy.sh)"
