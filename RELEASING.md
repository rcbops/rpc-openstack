# Release Process
- [ ] Create the tag.

  ```
  git tag -a -m 'Release VERSION' VERSION COMMIT
  git push REMOTE VERSION
  ```
- [ ] If creating an rc1 tag (the first release candidate) for a major or minor release:
  - [ ] Create a new branch.

    ```
    git branch RELEASE-MAJOR.MINOR NEW_TAG
    git push REMOTE RELEASE-MAJOR.MINOR
    ```
  - [ ] [Make the branch protected](https://github.com/rcbops/rpc-openstack/settings/branches). Copy the settings from one of the other protected branches. Access to settings is restricted, speak to a manager to get this step completed.

- [ ] If tagging the first version of a minor release, i.e. rX.Y.0, there will no longer be patch releases for the previous minor:
  - [ ] [Disable branch protection](https://github.com/rcbops/rpc-openstack/settings/branches) on the previous minor branch. Access to settings is restricted, speak to a manager to get this step completed.
  - [ ] Delete the old branch.

     ```
    git push REMOTE --delete OLD_BRANCH
    ```
- [ ] If creating or deleting a branch, update the [issue template](https://github.com/rcbops/rpc-openstack/blob/master/.github/ISSUE_TEMPLATE.md) to include it in the list.
- [ ] Update the [GitHub release notes](https://github.com/rcbops/rpc-openstack/releases) with output from rpc-differ, remember to tick pre-release if the tag is for a release candidate.

  ```
  rpc-differ --update PREVIOUS_TAG NEW_TAG | pandoc --from rst --to markdown_github
  ```
- [ ] [Close the old milestone](https://github.com/rcbops/rpc-openstack/milestones).
- [ ] [Create a new milestone](https://github.com/rcbops/rpc-openstack/milestones) and set a target date of 14 days from the date of the new tag.
- [ ] If this is a patch release, [create a docs issue](https://github.com/rackerlabs/docs-rpc) to get the release notes updated.
- [ ] Announce the release on opc mailing list.
