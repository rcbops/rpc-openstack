#!/bin/bash -xe

rpc-differ --debug -r "$REPO_URL" --update "$PREVIOUS_TAG" "$NEW_TAG" --file diff_notes.rst
pandoc --from rst --to markdown_github < diff_notes.rst > diff_notes.md
