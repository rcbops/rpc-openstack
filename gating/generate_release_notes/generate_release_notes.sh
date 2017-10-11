#!/bin/bash -xe

# This script is run within a docker container to generate release notes.

rpc-differ --debug -r "$REPO_URL" --update "$PREVIOUS_TAG" "$NEW_TAG" --file notes.rst
pandoc --from rst --to markdown_github < notes.rst > notes.md
