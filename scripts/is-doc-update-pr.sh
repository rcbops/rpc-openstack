#!/usr/bin/env bash
#
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

set -x
PREV_DIR=$PWD

usage() {
  echo "Determine if commit is documentation only change"
  echo "Usage: $0 [GIT-DIR]"
  echo -e "\n\tReturns:"
  echo -e "\t0  - Documentation only change"
  echo -e "\t1  - Not a documentation only change"
  echo -e "\t>1 - Error preventing ability to check"
}

if [ $# -gt 1 ] || [ $1 == "-h" ]; then
  usage
  exit 2
fi

if [ $1 ]; then
  # catch if invalid directory
  cd $1 || exit 2
fi

# Catch if invalid git repo
git status
if [ $? -eq 128 ]; then
  echo "Directory is not a git-repo, cannot check if changes are doc only"
  exit 128
fi

git show --stat=400,400 | awk '/\|/{print $1}' \
  | egrep -v -e '.*md$' -e '.*rst$' -e '^releasenotes/'
rc=$?

# return to previous directory if changed
if [ $PWD != ${PREV_DIR} ]; then
  cd ${PREV_DIR}
fi

case ${rc} in
  0)
    echo "Not a documentation only change or not triggered by a pull request"
    exit 1
    ;;
  1)
    echo "Only documentation changes detected"
    exit 0
    ;;
  *)
    echo "An unknown error occurred"
    exit 3
    ;;
esac
