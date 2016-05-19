#!/usr/bin/env bash
# Copyright 2015, Rackspace US, Inc.
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

## Shell Opts ----------------------------------------------------------------
set -euo pipefail

## Main ----------------------------------------------------------------------
if [[ -z "$VIRTUAL_ENV" ]] ; then
    echo "WARNING: Not running hacking inside a virtual environment."
fi

# NOTE(sigmavirus24): This allows us to utilize multiprocessing for the python
# files (for speed)
flake8 $(grep -rln -e '^#!/usr/bin/env python' \
                   -e '^#!/bin/python' \
                   -e '^#!/usr/bin/python' * )
# NOTE(sigmavirus24): This will run the git commit checks while ensuring that
# the commit error messages do not appear more than once (by constraining
# flake8 to not using multiprocessing). It's hacky but presently necessary
flake8 --ignore F403,H303 --jobs 0 hacking/
