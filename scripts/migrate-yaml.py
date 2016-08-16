#!/usr/bin/env python
# Copyright 2016, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# (c) 2016, Matthew Thode <matt.thode@rackspace.com>

"""
Print out values that have changed, by default just additions and changes.

Additions can be taken as is and placed into an overrides file, but should
you should verify you still want to keep it.

Removals are not printed by default because not having an override is the
same as taking a default.

Changes are printed, showing what you overrode and what is getting overridden.

CAUTION: danger-mode is only if you KNOW what you are overriding doesn't
    need to change, warrantee is void if used.
"""

from __future__ import print_function
import argparse
from collections import namedtuple
from deepdiff import DeepDiff
import yaml


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--overrides', dest='overrides', required=True,
                        help='The path to the file with overrides.')
    parser.add_argument('--info', dest='info', type=bool, default=False,
                        help='Shows what is NOT overridden.')
    parser.add_argument('--danger-mode', dest='danger',
                        type=bool, default=False,
                        help='Print output usable as an overrides file.')
    return parser.parse_args()


def root_cleanup(var):
    """Cleans up what deepdiff returns so we can have some cleaner output.

    :param var: the key you wish to clean up, just a string
    :return: the cleaned up string
    """
    prefix = "root['"
    suffix = "']"
    if var.startswith(prefix):
        var = var[len(prefix):]
    if var.endswith(suffix):
        var = var[:-len(suffix)]
    var = var.replace("']['", '.')
    return var


def parsed_yaml_from(path):
    """Load yaml data and return a python object

    :raises: IOError if the target path is invalid
    :raises: ParserError if the yaml is invalid
    :param path: path of yaml data to load
    :return: dictionary loaded from yaml data
    """
    try:
        with open(path) as f:
            data = f.read()
    except IOError:
        raise SystemExit('Error loading file: %s\n  Did you mistype?' % path)
    else:
        try:
            loaded_data = yaml.safe_load(data)
        except yaml.ParserError:
            raise SystemExit('The yaml in %s is non-compliant and failed'
                             'to load' % path)

    if loaded_data is None:
        return {}
    else:
        return loaded_data


def do_the_diff(defaults, overrides):
    """Diff two yaml loaded objects, returning diffs in a namedtuple

    :param defaults: File you wish to compare against, the base.
    :param overrides: File you wish to compare, the mask.
    :return: what is added, taken away, changed(added) and changed(removed).
    :rtype: namedtuple
    """
    added = {}
    removed = {}
    changed = {}
    changed_types = {}
    parsed_diff = namedtuple('parsed_yaml_diff',
                             ['added', 'removed',
                              'changed_added', 'changed_removed'])

    diff = DeepDiff(defaults, overrides, verbose_level=2)

    for old_key, value in diff.get('dictionary_item_added', {}).items():
        added[root_cleanup(old_key)] = value
    for old_key, value in diff.get('dictionary_item_removed', {}).items():
        removed[root_cleanup(old_key)] = value
    for old_key, value in diff.get('values_changed', {}).items():
        changed[root_cleanup(old_key)] = value
    for old_key, value in diff.get('type_changes', {}).items():
        changed_types[root_cleanup(old_key)] = value

    # Have to recast the values as dictionaries and combine type/value changes
    new_changed = {}
    new_changed_types = {}
    for key in changed:
        new_changed[key] = dict(changed[key])
    for key in changed_types:
        new_changed_types[key] = dict(changed_types[key])
    new_changed.update(new_changed_types)

    # we make two different yaml dump-able dictionaries, one for new values,
    # one for old (what is being overridden)
    new_changed_dict = {}
    old_changed_dict = {}
    for key in new_changed:
        new_changed_dict[key] = new_changed[key]['new_value']
        old_changed_dict[key] = new_changed[key]['old_value']

    return parsed_diff(added=added, removed=removed,
                       changed_added=new_changed_dict,
                       changed_removed=old_changed_dict)


def main(default_files):
    """Manage the work of loading the files and printing the output as needed

    :param default_files: A list of files to load data from
    :return: exits 0
    """
    args = parse_args()
    combined_defaults = {}

    # load the configs
    for value in default_files:
        combined_defaults.update(parsed_yaml_from(value))
    yaml_overrides = parsed_yaml_from(args.overrides)

    # get the actual diffs
    returned_diff = do_the_diff(combined_defaults, yaml_overrides)

    # print the diffs
    if args.danger:
        print('# Someone used danger-mode, this was not the best idea...')
        print('---')
    if returned_diff.added:
        if args.danger is False:
            print('==== added the following ====')
        print(yaml.safe_dump(dict(returned_diff.added),
                             default_flow_style=False))
    if args.info and args.danger is False:
        if returned_diff.removed:
            print('\n==== removed the following ====')
            print('==== you shouldn\'t have to care about this... ====')
            print(yaml.safe_dump(dict(returned_diff.removed),
                                 default_flow_style=False))
    if returned_diff.changed_added:
        if args.danger is False:
            print('\n==== changed the following (added) ====')
        print(yaml.safe_dump(returned_diff.changed_added,
                             default_flow_style=False))
    if returned_diff.changed_removed and args.danger is False:
        print('\n==== changed the following (removed) ====')
        print(yaml.safe_dump(returned_diff.changed_removed,
                             default_flow_style=False))


if __name__ == '__main__':
    path_prefix = '/opt/rpc-openstack/rpcd/etc/openstack_deploy/'
    files_to_load = [
        path_prefix + 'user_osa_variables_defaults.yml',
        path_prefix + 'user_rpco_variables_defaults.yml'
    ]
    main(files_to_load)
