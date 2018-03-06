# Copyright 2017, Rackspace US, Inc.
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

# Verify whether required plugins are installed.
required_plugins = [ "vagrant-disksize" ]
required_plugins.each do |plugin|
  if not Vagrant.has_plugin?(plugin)
    raise "The vagrant plugin #{plugin} is required. Please run `vagrant plugin install #{plugin}`"
  end
end

Vagrant.configure("2") do |config|
  config.vm.provider "virtualbox" do |v|
    v.memory = 12288
    v.cpus = 4
  end

  # Configure the disk size.
  disk_size = "100GB"

  config.vm.define "master" do |master|
    master.vm.box = "ubuntu/xenial64"
    master.disksize.size = disk_size
    master.vm.hostname = "rpco-master"
    config.vm.provision "shell",
      privileged: true,
      inline: <<-SHELL
        sudo su -
        apt update
        apt-get -y install git build-essential gcc libssl-dev libffi-dev python-dev
        git clone -b master --recursive https://github.com/rcbops/rpc-openstack.git /opt/rpc-openstack
        cd /opt/rpc-openstack/
        export DEPLOY_AIO=yes
        ./scripts/deploy.sh
      SHELL
  end

  config.vm.define "ocata" do |ocata|
    ocata.vm.box = "ubuntu/xenial64"
    ocata.disksize.size = disk_size
    ocata.vm.hostname = "rpco-ocata"
    config.vm.provision "shell",
      privileged: true,
      inline: <<-SHELL
        sudo su -
        apt update
        apt-get -y install git build-essential gcc libssl-dev libffi-dev python-dev
        git clone -b ocata --recursive https://github.com/rcbops/rpc-openstack.git /opt/rpc-openstack
        cd /opt/rpc-openstack/
        export DEPLOY_AIO=yes
        ./scripts/deploy.sh
      SHELL
  end

  config.vm.define "newton" do |newton|
    newton.vm.box = "ubuntu/xenial64"
    newton.disksize.size = disk_size
    newton.vm.hostname = "rpco-newton"
    config.vm.provision "shell",
      privileged: true,
      inline: <<-SHELL
        sudo su -
        apt update
        apt-get -y install git build-essential gcc libssl-dev libffi-dev python-dev
        git clone -b newton --recursive https://github.com/rcbops/rpc-openstack.git /opt/rpc-openstack
        cd /opt/rpc-openstack/
        export DEPLOY_AIO=yes
        ./scripts/deploy.sh
      SHELL
  end
end
