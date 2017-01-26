#!/usr/bin/env bash
#
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
set -x

## Functions -----------------------------------------------------------------

export BASE_DIR=${BASE_DIR:-"/opt/rpc-openstack"}
source ${BASE_DIR}/scripts/functions.sh

## Main ----------------------------------------------------------------------

# If the user_rpco_secrets.yml file exists in the user config, then merge that with
# the user_rpco_secrets.yml in tree. Otherwise, see if the user_extras_secrets.yml
# file exists and if so, use that.
if [[ -f "/etc/openstack_deploy/user_rpco_secrets.yml" ]]; then
  OVERRIDES="/etc/openstack_deploy/user_rpco_secrets.yml"
elif [[ -f "/etc/openstack_deploy/user_extras_secrets.yml" ]]; then
  OVERRIDES="/etc/openstack_deploy/user_extras_secrets.yml"
else
  echo "Cannot find user defined rpco secrets file! Please copy an rpco secrets file to /etc/openstack_deploy/"
  exit
fi

# Update the use-space secrets file with new secret variables
python2.7 ${BASE_DIR}/scripts/update-yaml.py \
    --output-file /etc/openstack_deploy/user_rpco_secrets.yml \
    $RPCD_DIR/etc/openstack_deploy/user_rpco_secrets.yml \
    $OVERRIDES

# Add values to any new secret variables
python2.7 $OA_DIR/scripts/pw-token-gen.py \
    --file /etc/openstack_deploy/user_rpco_secrets.yml
