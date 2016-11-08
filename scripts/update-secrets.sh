#!/bin/bash
set -x

export OA_DIR=${OA_DIR:-"$BASE_DIR/openstack-ansible"}
export RPCD_DIR=${RPCD_DIR:-"$BASE_DIR/rpcd"}

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

python2.7 /opt/rpc-openstack/scripts/update-yaml.py --output-file /etc/openstack_deploy/user_rpco_secrets.yml $RPCD_DIR/etc/openstack_deploy/user_rpco_secrets.yml $OVERRIDES
python2.7 $OA_DIR/scripts/pw-token-gen.py --file /etc/openstack_deploy/user_rpco_secrets.yml
