#!/bin/bash -xe

# This script is run within a docker container to generate release notes.

url=$(git remote -v |awk '/origin.*fetch/{print $2}')
rpc-differ --debug -r "$url" --update "$PREVIOUS_TAG" "$NEW_TAG" --file notes.rst
pandoc --from rst --to markdown_github < notes.rst > notes.md
