#!/usr/bin/env python
# Copyright 2014-2017, Rackspace US, Inc.
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

import os
import subprocess
import shutil
import tempfile

import yaml


__doc__ = """Script usage.
Export the environment variable "ROLE_REQUIREMENTS_FILE" with the path to a
known ansible role requirements file. The items within the file will be read
and anything that is using the "git" "scm" setting it will clone extract the
last "SHA" from a given branch. By default this script will assume the repo
within the role requirements file is tracking the "master" branch however if
a different branch is desired set the "branch" option in the role
requirements file to whatever branch the system should track.

Example entry:
- name: role-name
  scm: git
  src: https://github.com/rcbops/role-name.git
  version: XXXX

Example entry setting the tracking branch:
- name: role-name
  scm: git
  src: https://github.com/rcbops/role-name.git
  version: XXXX
  branch: stable
"""


class TempDirMake(object):
    def __init__(self):
        """Create a temp workspace and cleanup on exit.

        This class creates a context manager which makes a temp workspace and
        cleans up when the context manager exits.

        Entering the context manager returns the temp workspace path as a
        string.
        """
        self.temp_dir = None
        self.cwd = None

    def __enter__(self):
        os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.temp_dir)
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.temp_dir)
        os.chdir(self.cwd)


# Read the file contents
requirements_file = os.environ['ROLE_REQUIREMENTS_FILE']


with open(requirements_file) as f:
    release_file_content = yaml.safe_load(f.read())


with TempDirMake() as mkd:
    for item in release_file_content:
        if item['scm'] != 'git':
            pass

        branch = item.get('branch', 'master')
        src = item['src']

        subprocess.call(
            ["git", "clone", src],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        os.chdir(os.path.basename(src.split('.git')[0]))
        subprocess.call(
            ["git", "checkout", branch],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        p = subprocess.check_output(['git', 'log', '-n', '1', '--format=%H'])
        item['version'] = p.strip()


with open(requirements_file, 'w') as f:
    f.write(
        yaml.safe_dump(
            release_file_content, default_flow_style=False, width=1000))
