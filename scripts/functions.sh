#!/usr/bin/env bash

export ANSIBLE_PARAMETERS=${ANSIBLE_PARAMETERS:-''}
export FORKS=${FORKS:-$(grep -c ^processor /proc/cpuinfo)}

export RPCM_VARIABLES='/etc/openstack_deploy/user_rpcm_variables.yml'

export RPCD_DIR='/opt/rpc-openstack/rpcd'

function run_ansible {
  openstack-ansible ${ANSIBLE_PARAMETERS} --forks ${FORKS} $@
}

function add_config {
  src="$1"
  src_path="${BASE_DIR}/scripts/config/${src}.yml"
  if [[ -e "${src_path}" ]]; then
      echo "Adding vars from $src_path to $RPCD_VARS: $(cat $src_path)"
      cat ${src_path} >> $RPCD_VARS
  else
    echo "$src_path not found, no vars added to $RPCD_VARS"
  fi
}
