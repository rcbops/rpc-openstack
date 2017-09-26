# Artifacts documentation

#### Overview

RPC-O builds and uses the following artifacts:

* apt: All the apt repositories used in RPC-O and OpenStack-Ansible (OSA) are
  aggregated into a single apt repository using
  [aptly](https://www.aptly.info/). The reason for doing this is to ensure
  that every single deployment of RPC-O uses exactly the same apt packages
  for each release.

* git: All the git repositories which are synchronised by the repo container
  are artifacted as compressed tarballs so that they are quicker and more
  reliable to download.

* python: All python wheels and venvs are built using the apt artifacts so
  that these can be used across all RPC-O environments.

* container: Using the apt and python artifacts, most roles implemented in
  RPC-O have a container variant chroot prepared so that deployments can
  consume them to ensure consistency across all RPC-O environments.

Artifacts in RPC-O are both built and consumed using scripts in this
directory.

#### Artifact Build Process

The CI process which builds RPC-O artifacts executes them in a specific
order to ensure that each artifact is using the previous artifacts which
were built.

1. Apt artifacts are built. This is done per RPC-O series and published
   using the value for ``rpc_release`` and the distribution code name.
   Current apt repositories available can be found on
   [rpc-repo](http://rpc-repo.rackspace.com/apt-mirror/integrated/dists/).

   The upstream apt repositories to mirror are all set in
   ``scripts/artifacts-building/apt/aptly-vars.yml`` in the ``aptly_mirrors``
   variable. They are combined into snapshots per release, then combined into
   an integrated snapshot as specified in the variable ``aptly_miko_mapping``.

   Some packages are not built properly for multiple distributions. They are
   built using the same package name, same version number, but different
   contents for each distribution. The repositories for these packages are
   published independently and can be found on
   [rpc-repo](http://rpc-repo.rackspace.com/apt-mirror/independant/).
   These are defined in the ``aptly_n_mapping`` variable.

   Only one Apt artifact build can be executed at a time across all
   series/tests as the test executes on a long running host which has
   aptly installed. Aptly's CLI locks the database and can therefore only
   execute one job at a time. The job executes
   ``scripts/artifacts-building/apt/build-apt-artifacts.sh``.

2. Git artifacts are built. This is per RPC-O series and published using
   the value for ``rpc_release``. Published artifacts can be found on
   [rpc-repo](http://rpc-repo.rackspace.com/git-archives/). The job
   executes ``scripts/artifacts-building/git/build-git-artifacts.sh``.

3. Python artifacts are built using the previously built apt artifacts.
   This is necessary as some wheels are linked to specific C libraries
   and therefore the matching of a specific wheel version to a specific
   apt package is important. This is done using a partial RPC-O AIO (only
   the repo server is built) using the standard repo-build playbook from
   OSA, but with selective git cloning, selective wheel building and
   selective venv building disabled so that we have packages and venvs
   for everything supported by RPC-O. Published artifacts can be found
   on [rpc-repo](http://rpc-repo.rackspace.com/os-releases/). The job
   executes ``scripts/artifacts-building/python/build-python-artifacts.sh``.

4. Container artifacts are built using the previously built apt and python
   artifacts. This is done by preparing the host as a LXC host, then building
   a series on containers in turn without starting them but instead executing
   the appropriate roles against them using a chroot connection and tagfilter
   strategy. The tagfilter strategy ignores all ``-config`` tasks and filters
   out all notifiers so that the chroot only has the right apt packages
   installed and the right python packages and venvs installed. Published
   artifacts can be found on
   [rpc-repo](http://rpc-repo.rackspace.com/lxc-images/). The job executes
   ``scripts/artifacts-building/containers/build-process.sh``.


#### Artifact Build Tests

As RPC-O executes deploy tests in PR's where the value for ``rpc_release`` is
being changed in the PR, the artifact build scripts have been designed to
adapt based on whether the previous artifacts exist for the given release or
not.

The PR tests are implemented in parallel so that they give results back
quickly. They are designed to simply exercise the build scripts to verify
that changes are not breaking them. The PR tests are all read-only - they
do not upload any results to rpc-repo.

Periodic jobs are designed to build new artifacts in the proper sequence,
ensuring that artifacts which depend on each other are built using their
dependencies. If a set of artifacts does not already exist on rpc-repo
for the given ``rpc_release``, the periodic job will upload artifacts
for it if the build is successful. To replace artifacts for a series,
execute the periodic job for the series with ``REPLACE_ARTIFACTS`` set to
``YES``.

#### Artifact Consumption Process

Artifacts are consumed by implementing the appropriate variable overrides for
OSA to consume our artifacts instead of using the default upstream artifacts.

* Apt artifact consumption configuration is implemented in
  ``group_vars/all/apt.yml`` and in the lower part of
  ``rpcd/etc/openstack_deploy/user_rpco_variables_defaults.yml``.

* Git and python artifacts are staged using
  ``rpcd/playbooks/stage-python-artifacts.yml``, then consumed as they are in
  any normal RPC-O/OSA deployment. The RPC-O deployment script skips the
  repo-build playbook to save time, but changes in the repo-build process in
  OSA mean that if the repo-build playbook is run it will skip all the build
  processes anyway as long as none of the requirements have changed.

* Container artifact consumption is implemented through the use of the
  ``lxc_container_variant`` variable set for each group in group vars, and
  various global settings implemented in ``group_vars/all/lxc.yml``. These
  settings instruct LXC to use the RPC-O prepared chroots when building the
  container instead of using the upstream LXC container base.

As RPC-O executes build tests in PR's where the value for ``rpc_release`` is
being changed in the PR, the AIO build process has been designed to adapt
based on whether artifacts exist for the given release or not.

