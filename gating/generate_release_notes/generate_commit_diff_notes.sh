#!/bin/bash -xe
source "scripts/functions.sh"

rpc-differ --debug -rp ${RPC_PRODUCT_RELEASE} -rr "ansible-role-${RPC_PRODUCT_RELEASE}-requirements.yml" -r "$REPO_URL" --update "$PREVIOUS_TAG" "$NEW_TAG" --file diff_notes.rst
pandoc --from rst --to markdown_github < diff_notes.rst > diff_notes.md
