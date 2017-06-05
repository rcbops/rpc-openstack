#!/usr/bin/env bash

export ANSIBLE_PARAMETERS=${ANSIBLE_PARAMETERS:-''}
export FORKS=${FORKS:-$(grep -c ^processor /proc/cpuinfo)}

export RPCM_VARIABLES='/etc/openstack_deploy/user_rpcm_variables.yml'

export RPCD_DIR='/opt/rpc-openstack/rpcd'

function run_ansible {
  openstack-ansible ${ANSIBLE_PARAMETERS} --forks ${FORKS} $@
}
