#!/bin/bash

## Shell Opts ----------------------------------------------------------------

set -euv
set -o pipefail

## Main ----------------------------------------------------------------------

# Jenkins automatically clones the repository and initialises any submodules.
# tox is currently being used to run lint checkers that should not be checking
# submodule code or other checks that do not require them.
git submodule deinit .

apt-get update
apt-get install -y wget

pip install 'tox!=2.4.0,>=2.3'

tmp_tox_dir=$(mktemp -d)
tox -e $RE_JOB_SCENARIO --workdir $tmp_tox_dir
