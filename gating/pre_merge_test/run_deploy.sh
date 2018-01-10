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
  DEBIAN_FRONTEND=noninteractive apt-get -y upgrade

elif [[ ${RE_JOB_IMAGE} =~ loose_artifacts$ ]]; then
  # Set the apt artifact mode
  export RPC_APT_ARTIFACT_MODE="loose"

  # Upgrade to the absolute latest
  # available packages.
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get -y upgrade
fi

## Functions -----------------------------------------------------------------

## Main ----------------------------------------------------------------------

# Run the deployment script
bash -c "$(readlink -f $(dirname ${0})/../../scripts/deploy.sh)"
