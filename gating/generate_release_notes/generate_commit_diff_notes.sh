#!/bin/bash -xe

# Set the base RPC-O directory which the functions use
export BASE_DIR="${PWD}"

# Source the functions
source "${BASE_DIR}/scripts/functions.sh"


if echo ${PREVIOUS_TAG} | egrep '^r[0-9]+\.'; then
  PREVIOUS_RPC_PRODUCT_RELEASE="$(component release --component-name rpc-openstack get --version ${PREVIOUS_TAG} | grep 'series:' | awk '{print $2}')"
else
  # Assume PREVIOUS_TAG is one of the release branches
  PREVIOUS_RPC_PRODUCT_RELEASE="${PREVIOUS_TAG}"
fi

rpc-differ \
  --debug \
  -rpoc ${PREVIOUS_RPC_PRODUCT_RELEASE} \
  -rroc "ansible-role-${PREVIOUS_RPC_PRODUCT_RELEASE}-requirements.yml" \
  -rp ${RPC_PRODUCT_RELEASE} \
  -rr "ansible-role-${RPC_PRODUCT_RELEASE}-requirements.yml" \
  -r "$REPO_URL" \
  --update \
  "$PREVIOUS_TAG" \
  "$NEW_TAG" \
  --file diff_notes.rst
pandoc --from rst --to markdown_github < diff_notes.rst > diff_notes.md
