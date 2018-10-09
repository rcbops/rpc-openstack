#!/bin/bash

## Shell Opts ----------------------------------------------------------------

set -eux
set -o pipefail

## Vars & Functions ----------------------------------------------------------

export BASE_DIR=${BASE_DIR:-"/opt/rpc-openstack"}
source ${BASE_DIR}/scripts/functions.sh
source "$(readlink -f $(dirname ${0}))/../gating_vars.sh"

## Main ----------------------------------------------------------------------

echo "#### BEGIN LOG COLLECTION ###"

collect_logs_cmd="ansible-playbook"
collect_logs_cmd+=" --ssh-common-args='-o StrictHostKeyChecking=no'"
collect_logs_cmd+=" --extra-vars='artifacts_dir=${RE_HOOK_ARTIFACT_DIR}'"
collect_logs_cmd+=" --extra-vars='result_dir=${RE_HOOK_RESULT_DIR}'"

if [[ ${RE_JOB_IMAGE} =~ .*mnaio.* ]]; then
  collect_logs_cmd+=" --extra-vars='target_hosts=pxe_servers'"
  collect_logs_cmd+=" --inventory='/opt/openstack-ansible-ops/multi-node-aio/playbooks/inventory/hosts'"
else
  collect_logs_cmd+=" --extra-vars='target_hosts=localhost'"
fi

collect_logs_cmd+=" $(dirname ${0})/collect_logs.yml"

eval $collect_logs_cmd || true

echo "#### END LOG COLLECTION ###"

extract_rpc_release(){
  awk '/rpc_release/{print $2}' | tr -d '"'
}

# Only enable snapshot when triggered by a commit push.
# This is to enable image updates whenever a PR is merged, but not before
if [[ "${RE_JOB_TRIGGER:-USER}" == "PUSH" ]] && [[ ${RE_JOB_STATUS:-SUCCESS} == "SUCCESS" ]]; then
  echo "### BEGIN SNAPSHOT PREP ###"
  mkdir -p /gating/thaw

  # /opt/rpc-openstack may be a symlink to $WORKSPACE/rpc-openstack
  # However $WORKSPACE will be wiped prior to the snapshot being taken
  # so will not be present in instances created from the snapshot.
  # In order to ensure /opt/rpc-openstack is present in the snapshot
  # We check if its a link if it is, unlink it and create a full copy.
  pushd /opt
  target="$(readlink -f rpc-openstack)"
  if [[ -n "$target" ]]; then
      echo "/opt/rpc-openstack is linked into $WORKSPACE/rpc-openstack which"
      echo "will be wiped prior to creating a snapshot."
      echo "Removing symlink and copying $WORKSPACE/rpc-openstack to /opt."
      rm rpc-openstack
      cp -ar $target rpc-openstack
  fi

  # /root/.ssh is cleared on thaw. We need to store the keys that were there.
  mkdir -p /opt/root_ssh_backup
  cp -vr /root/.ssh /opt/root_ssh_backup

  ln -s /opt/rpc-openstack/gating/thaw/run /gating/thaw/run

  rpc_release="$(extract_rpc_release </opt/rpc-openstack/group_vars/all/release.yml)"

  echo "rpc-${RPC_RELEASE}-${RE_JOB_IMAGE}-${RE_JOB_SCENARIO}" > /gating/thaw/image_name
  echo "### END SNAPSHOT PREP ###"
fi

if [[ ${RE_JOB_IMAGE} =~ .*mnaio.* ]] && [[ ${RE_JOB_ACTION} == "deploy" ]] && [[ "${RE_JOB_STATUS:-SUCCESS}" == "SUCCESS" ]]; then
  echo "Preparing machine image artifacts."
  pushd /opt/openstack-ansible-ops/multi-node-aio
    ansible-playbook -vv -i ${MNAIO_INVENTORY:-"playbooks/inventory"} playbooks/save-vms.yml
  popd

  echo "Deleting unnecessary image files to prevent artifacting them."
  find /data/images -name \*.img -not -name \*-base.img -delete

  echo "Moving files to named folder for artifact upload."
  mv /data/images /data/${RPC_RELEASE}-${RE_JOB_IMAGE}-${RE_JOB_SCENARIO}

  echo "Preparing machine image artifact upload configuration."
  cat > component_metadata.yml <<EOF
"artifacts": [
  {
    "type": "file",
    "source": "/data/${RPC_RELEASE}-${RE_JOB_IMAGE}-${RE_JOB_SCENARIO}"
  }
]
EOF
fi
