# Leapfrog Documentation

## Leapfrog Upgrade scripts have moved!

Leapfrogs have moved to their own dedicated repo at [rpc-upgrades](https://github.com/rcbops/rpc-upgrades).

## Overview

A Leapfrog upgrade is a major upgrade that skips at least one release. Currently RPCO supports leapfrog upgrades from kilo to r14.2.0 (newton).

## Quick Start for Leaping from Kilo/Liberty on RPC-O

To get a leapfrog upgrade started, from the deploy host:

    git clone https://github.com/rcbops/rpc-upgrades.git /opt/rpc-upgrades
    cd /opt/rpc-upgrades/scripts
    ./ubuntu14-leapfrog.sh

## Documentation
### RPC-O Leapfrog Docs

* [README](https://github.com/rcbops/rpc-upgrades/blob/master/README.rst)
* [Testing](https://github.com/rcbops/rpc-upgrades/blob/master/testing.rst)

### Upstream Leapfrog Docs

* [README](https://github.com/openstack/openstack-ansible-ops/blob/master/leap-upgrades/README.md)
