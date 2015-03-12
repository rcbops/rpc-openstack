#!/usr/bin/env python
import os
import sys
import subprocess
import yaml


def get_rpc_repo_path():
    """
    Return the 'rpc_repo_path' configuration setting.
    The function looks for this setting in the following config files:
        1. /etc/openstack_deploy/user_extras_variables.yml
        2. $HOME/openstack_deploy/user_extras_variables.yml
        3. rpc_extras/playbooks/group_vars/all.yml
    If the setting isn't found on any of these files then None is returned.
    """
    basedir = os.path.abspath(os.path.dirname(__file__))
    file_check = [
        '/etc/openstack_deploy/user_extras_variables.yml',
        os.path.join(os.environ.get('HOME'),
                     'openstack_deploy/user_extras_variables.yml'),
        os.path.join(basedir, '../group_vars/all.yml')
    ]

    for f in file_check:
        if os.path.isfile(f):
            with open(f, 'r') as s:
                cfg = yaml.load(s)
                if 'rpc_repo_path' in cfg:
                    return cfg['rpc_repo_path']
    return None

rpc_repo_path = get_rpc_repo_path()
if rpc_repo_path is None:
    raise SystemExit('rpc_repo_path not found')
rpc_inventory = os.path.join(rpc_repo_path,
                             'playbooks/inventory/dynamic_inventory.py')
subprocess.call([rpc_inventory] + sys.argv[1:])
