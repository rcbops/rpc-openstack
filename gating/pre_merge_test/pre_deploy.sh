#!/bin/bash

## Shell Opts ----------------------------------------------------------------

set -e -u -x
set -o pipefail

## Vars ----------------------------------------------------------------------
export KIBANA_SELENIUM_REPO="https://github.com/rcbops-qe/kibana-selenium"
export KIBANA_SELENIUM_BRANCH="liberty"

## Main ----------------------------------------------------------------------

# If the current folder's basename is rpc-openstack then we assume
# that it is the root of the git clone. If the git clone is not in
# /opt then we symlink the current folder there so that all the
# rpc-openstack scripts work as expected.
if [[ "$(basename ${PWD})" == "rpc-openstack" ]]; then
  if [[ "${PWD}" != "/opt/rpc-openstack" ]]; then
    ln -sfn ${PWD} /opt/rpc-openstack
  fi
fi

# Clone the kibana-selenium git repository
git clone -b ${KIBANA_SELENIUM_BRANCH} ${KIBANA_SELENIUM_REPO} /opt/kibana-selenium

# Prepare for Kibana Selenium Tests
cd /opt/kibana-selenium

# The phantomjs package on 16.04 is buggy, see:
# https://github.com/ariya/phantomjs/issues/14900
# https://bugs.launchpad.net/ubuntu/+source/phantomjs/+bug/1578444
#apt-get install -y phantomjs
apt-get install -y fontconfig
wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
tar -xjf phantomjs-2.1.1-linux-x86_64.tar.bz2
if [[ ! -d ".venv" ]]; then
  pip install virtualenv
  virtualenv .venv
fi

# Work around https://github.com/pypa/virtualenv/issues/1029
export VIRTUAL_ENV_DISABLE_PROMPT=true

set +x; source .venv/bin/activate; set -x

if [ -f ~/.pip/pip.conf ]; then
  mv ~/.pip/pip.conf ~/.pip/pip.conf.bak
  pip install -r requirements.txt
  mv ~/.pip/pip.conf.bak ~/.pip/pip.conf
else
  pip install -r requirements.txt
fi
