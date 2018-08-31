#!/bin/bash

## Shell Opts ----------------------------------------------------------------

set -e -u -x
set -o pipefail

## Vars ----------------------------------------------------------------------
export KIBANA_SELENIUM_REPO="https://github.com/rcbops-qe/kibana-selenium"
export KIBANA_SELENIUM_BRANCH="newton"

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

if [[ $RE_JOB_IMAGE =~ .*mnaio.* ]]; then
  # We need to ensure that we use the rackspace mirrors, as they are
  # most reliable. We also need to ensure that python and the python
  # yaml library are present for ansible to work. This is implemented
  # only for MNAIO tests as AIO's use artifacts and already have the
  # right things implemented in the images they use.
  source "$(readlink -f $(dirname ${0}))/pre_deploy_mnaio.sh"
fi

# Clone the kibana-selenium git repository
if [[ ! -e /opt/kibana-selenium ]]; then
  git clone -b ${KIBANA_SELENIUM_BRANCH} ${KIBANA_SELENIUM_REPO} /opt/kibana-selenium
fi

# Prepare for Kibana Selenium Tests
cd /opt/kibana-selenium

# Install pre-requisites
pkgs_to_install=""
# The phantomjs package on 16.04 is buggy, see:
# https://github.com/ariya/phantomjs/issues/14900
# https://bugs.launchpad.net/ubuntu/+source/phantomjs/+bug/1578444
#dpkg-query --list | grep phantomjs &>/dev/null || pkgs_to_install+="phantonjs "
dpkg-query --list | grep fontconfig &>/dev/null || pkgs_to_install+="fontconfig "
if [[ $(lsb_release -cd | grep Codename | awk '{print $2}') == "trusty" ]]; then
  virtualenv --version &>/dev/null || pkgs_to_install+="python-virtualenv "
else
  virtualenv --version &>/dev/null || pkgs_to_install+="python-virtualenv virtualenv "
fi
if [ "${pkgs_to_install}" != "" ]; then
  apt-get update
  apt-get install -y ${pkgs_to_install}
fi

if [[ ! -e phantomjs-2.1.1-linux-x86_64.tar.bz2 ]]; then
  wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
  tar -xjf phantomjs-2.1.1-linux-x86_64.tar.bz2
fi

if [[ ! -d ".venv" ]]; then
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
