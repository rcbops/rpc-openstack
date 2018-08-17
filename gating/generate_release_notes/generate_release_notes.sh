#!/bin/bash -xe

gating/generate_release_notes/generate_commit_diff_notes.sh
gating/generate_release_notes/generate_reno_report.sh $NEW_TAG reno_report.md
cat reno_report.md diff_notes.md > all_notes.md
