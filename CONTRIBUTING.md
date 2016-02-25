# Contributing to this repository

#### Notes
- ```master``` branch is always the 'current' branch where development for the next minor or major release is taking place
- named branches (e.g. ```liberty-12.1```, or ```mitaka-13.2```) are release branches where releases are tagged
- All branches have gating enabled, and patches should not be merged that do not pass gating
- QE testing is only performed on major (e.g. ```12.0.0```) and minor (e.g. ```12.1.0```) releases, not on patch (e.g. ```12.1.5```) releases, which are assumed to be adequately tested by the commit based, and periodic, jenkins gating.

##### Version definitions

**Major.minor.patch**

* Major
  * openstack release
  * possibly feature?
* minor
  * big change within release
  * security  - upgrade-impacting
  * bug fixes - upgrade-impacting
  * features
  * sha bumps
* patch
  * security  - non-upgrade-impacting
  * bug fixes - non-upgrade-impacting

## Working in the repository

### filing a bug report

When creating an issue, please ensure you include the following information

* branch (or tag) on which you encountered this issue
* Steps to reproduce
* Any output or logs that you gathered from your environment

### fixing a bug

1. A bug is filed or feature requested against ```rpc-openstack```
2. After triage and prioritisation, the developer pushes a fix directly to a branch on ```rpc-openstack``` in the ```rcbops``` github namespace (rather than a developers own fork). A pull request is then made from this branch to the ```master``` branch.
3. Unless a bug is specific to a release branch (e.g. ```liberty-12.1```), fixes are made to the ```master``` branch before any potential backports.
4. Bugs meeting backport criteria are backported to the release branches (e.g. ```liberty-12.1```) as appropriate.
5. github markdown is used to update the original issue with a checklist for tracking which branches have had fixes merged.
6. Each time a PR is merged, the associated branch is deleted from ```rpc-openstack```.
7. When all PRs are completed the issue is then closed.

### reviewing a fix

When reviewing, please ensure the fix:

* actually works to fix the issue
* passes the gate checks that are configured to run
* Contains a single commit, which itself has a good commit message describing the changes involved in the patch
* Does not overreach - each commit should be self contained enough to only address the issue at hand, and no more.

### merging a fix

In order for a fix to be merged, the following criteria should be met:

* all gate tests must have passed
* There must be at least 2 reviewers (members of the rcbops engineering team) who have given it the thumbsup/+1 (using the review guidelines above)
* The second of those +1 reviewers should merge the patch


## release workflow

### major/minor releases
1. work (meaning bugfixes and feature development) is performed in the ```master``` branch in preparation for a major or minor release (e.g. ```12.0.0``` or ```12.2.0```)
2. When all criteria for the targeted release are fulfilled, a release branch is created using the naming convention **series-Major.minor** (e.g. ```liberty-12.0```, or ```mitaka-13.1```), and an rc tag created (e.g. ```r12.0.0rc1```). This tag is then passed to the QE team for initial testing
3. Work continues in ```master``` on features and bugs targeted at the next major or minor release (e.g. ```12.1.0```)
4. As QE (and potentially support and other teams) progress their testing on the release candidate, bugs will be identified in the rc tag that was handed to them. These bugs should be fixed in ```master``` and cherry-picked to the release branch. **No other bug fixes should be cherry-picked into this branch** so that this branch can remain a non-moving target for QE.
5. Once all bugs from the initial release candidate have been cherry-picked into the release branch, a new release candidate should be tagged (e.g. ```r12.0.0rc2```)
6. Steps 4-5 should be repeated until the latest rc passes all QE tests satisfactorily.
7. Once QE are satisfied, a release tag (e.g. ```r12.0.0```) is created in the release branch

### patch releases
1. Work (bugfixes) is performed in the ```master``` branch and cherry-picked into the release branch (e.g. ```liberty-12.1``` or ```mitaka-13.1```). OR work (bugfixes) is performed directly in the release branch if it is release specific and doesn't affect ```master```.
2. Every 2 weeks (approximately) a new release tag (e.g. ```12.1.1```) is made.
3. Immediately after tagging, all external projects included either via submodules, ansible-galaxy or some other mechanism, will have the version/revision/SHA updated to point to the HEAD of that project (in vernacular, we'll do a SHA bump). This allows an immediate set of gate jobs to run on those SHA bumps, as well as the next 2 weeks of development to happen against those new SHA's. This will allow us to stay current and only have to cope with incremental change in external projects. 

[1]
```
sample markdown for checklist

---
- [x] master PR: https://github.com/rcbops/rpc-openstack/pull/{{number}}
- [] kilo PR: https://github.com/rcbops/rpc-openstack/pull/{{number}}
```

