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

# -------------- Import ---------------------#
export BASE_DIR=${BASE_DIR:-"/opt/rpc-openstack"}
source ${BASE_DIR}/scripts/functions.sh
# ------------ End import -------------------#

export WORKSPACE=${WORKSPACE:-"$HOME"}

echo "Archiving logs and configs..."
d="${WORKSPACE}/logs"
mkdir -p $d

# logs and config from host
mkdir -p $d/$HOSTNAME/log
cp -rp /openstack/log/$HOSTNAME-* $d/$HOSTNAME/log ||:
cp -rp /etc/ $d/$HOSTNAME/etc
cp -rp /var/log/ $d/$HOSTNAME/var_log

# logs and config from the containers
while read c; do
  mkdir -p $d/$c/log
  cp -rp /openstack/log/$c/* $d/$c/log 2>/dev/null ||:
  cp -rp /var/lib/lxc/$c/rootfs/etc $d/$c 2>/dev/null ||:
  cp -rp /var/lib/lxc/$c/delta0/etc $d/$c 2>/dev/null ||:
done < <(lxc-ls)

# compress to reduce storage space requirements
ARTIFACT_SIZE=$(du -sh $d | cut -f1)
echo "Compressing $ARTIFACT_SIZE of artifact files..."
tar cjf "$d".tar.bz2 $d
echo "Compression complete."
rm -rf ${d}
