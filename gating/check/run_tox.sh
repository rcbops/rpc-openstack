#!/bin/bash

## Shell Opts ----------------------------------------------------------------

set -euv
set -o pipefail

## Main ----------------------------------------------------------------------

apt-get update
apt-get install -y wget

pip install 'tox!=2.4.0,>=2.3'

tmp_tox_dir=$(mktemp -d)
tox -e $RE_JOB_SCENARIO --workdir $tmp_tox_dir
