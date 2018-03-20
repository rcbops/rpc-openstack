#!/bin/bash

## Shell Opts ----------------------------------------------------------------

set -eux
set -o pipefail

## Vars ----------------------------------------------------------------------

export DEPLOY_AIO="true"

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

## Functions -----------------------------------------------------------------

## Main ----------------------------------------------------------------------

# Run the deployment script
bash -c "$(readlink -f $(dirname ${0})/../../scripts/deploy.sh)"
