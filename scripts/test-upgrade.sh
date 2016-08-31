#!/usr/bin/env bash
# Copyright 2014, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# (c) 2015, Nolan Brubaker <nolan.brubaker@rackspace.com>

set -eux -o pipefail

BASE_DIR=$( cd "$( dirname ${0} )" && cd ../ && pwd )
OA_DIR="$BASE_DIR/openstack-ansible"
RPCD_DIR="$BASE_DIR/rpcd"

# TASK #1
# Bug: https://github.com/rcbops/u-suk-dev/issues/199
# Issue: To avoid any dependency issues that have occured in the past, the
#        repo_server containers are re-built. This was done as part of the
#        OSA upgrade script in liberty, but is not done in the OSA mitaka
#        upgrade script. Thus, we destroy the containers here.
cd ${OA_DIR}/playbooks
openstack-ansible lxc-containers-destroy.yml --limit repo_all
openstack-ansible setup-hosts.yml --limit repo_all
