#!/bin/bash -xe

rpc-differ --debug -r "$REPO_URL" --update --osa-repo-url https://github.com/rcbops/openstack-ansible "$PREVIOUS_TAG" "$NEW_TAG" --file diff_notes.rst
pandoc --from rst --to markdown_github < diff_notes.rst > diff_notes.md
