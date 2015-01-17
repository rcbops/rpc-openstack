#!/usr/bin/env python
import os
import sys
import subprocess

basedir = os.path.abspath(os.path.dirname(__file__))
rpc_inventory = os.path.join(
    basedir, ('../../../os-ansible-deployment/rpc_deployment/inventory/'
              'dynamic_inventory.py'))
subprocess.call([rpc_inventory] + sys.argv[1:])
