#!/usr/bin/env bash
source /opt/rpc-extras/os-ansible-deployment/scripts/scripts-library.sh

export RPCD_LOGSTASH=${RPCD_LOGSTASH:-"FALSE"}
export RPCD_AIO=${RPCD_AIO:-"FALSE"}

OSAD_DIR='/opt/rpc-extras/os-ansible-deployment'
RPCD_DIR='/opt/rpc-extras/rpcd'

# setup the things
cd "${OSAD_DIR}" || exit_fail
if [ "${RPCD_AIO}" == "yes" ]; then
  ./scripts/bootstrap-aio.sh || exit_fail
  cp -R "${RPCD_DIR}"/etc/openstack_deploy/* /etc/openstack_deploy/ || exit_fail
fi
./scripts/bootstrap-ansible.sh || exit_fail
./scripts/pw-token-gen.py --file /etc/openstack_deploy/user_extras_secrets.yml || exit_fail
cd "${OSAD_DIR}"/playbooks/ || exit_fail
install_bits setup-hosts.yml || exit_fail
if [ "${RPCD_AIO}" == "yes" ]; then
  install_bits haproxy-install.yml || exit_fail
fi
install_bits setup-infrastructure.yml setup-openstack.yml || exit_fail

# setup the rest
cd "${RPCD_DIR}"/playbooks/ || exit_fail
install_bits horizon_extensions.yml rpc-support.yml setup-maas.yml || exit_fail
if [ "${RPCD_LOGSTASH}" == "yes" ]; then
  install_bits setup-logging.yml || exit_fail
fi
