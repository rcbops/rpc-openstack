#!/bin/bash

## Shell Opts ----------------------------------------------------------------

set -eux
set -o pipefail

## Vars ----------------------------------------------------------------------

export DEPLOY_AIO="true"

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
