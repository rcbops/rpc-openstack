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
Write a file containing new overrides with the new defaults stripped from the
old overrides and conflicts listed in their own keys.
"""

from __future__ import print_function
import argparse
import os
import yaml


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--overrides', dest='overrides', required=True,
                        help='The path to the file with overrides.')
    parser.add_argument('--defaults', dest='defaults', required=True,
                        help='The path to the file with defaults.')
    parser.add_argument('--output-file', dest='output_file', required=True,
                        help='The path to the new overrides file location')
    parser.add_argument('--for-testing-take-new-vars-only', dest='testing',
                        action="store_true",
                        help="don't take old overrides over new defaults")
    return parser.parse_args()


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
        except yaml.parser.ParserError:
            raise SystemExit('The yaml in %s is non-compliant and failed '
                             'to load' % path)

    if loaded_data is None:
        return {}
    else:
        return loaded_data


def do_the_diff(defaults, overrides):
    """Diff two yaml loaded objects, returning diffs in a namedtuple

    :param defaults: File you wish to compare against, the base.
    :param overrides: File you wish to compare, the mask.
    :return: stuff
    :rtype: dict
    """

    new_combined_diff = {}

    for key in overrides.keys():
        if key not in defaults.keys():
            new_combined_diff[key] = overrides[key]
        else:
            if defaults[key] == overrides[key]:
                pass
            else:
                if 'NEW_DEFAULTS' not in new_combined_diff.keys():
                    new_combined_diff['NEW_DEFAULTS'] = {}
                if 'OLD_OVERRIDES' not in new_combined_diff.keys():
                    new_combined_diff['OLD_OVERRIDES'] = {}
                new_combined_diff['NEW_DEFAULTS'][key] = defaults[key]
                new_combined_diff['OLD_OVERRIDES'][key] = overrides[key]

    return new_combined_diff


def main():
    """Manage the work of loading the files and printing the output as needed

    :return: exits 0
    """
    args = parse_args()

    # get the actual diffs
    returned_combined = do_the_diff(defaults=parsed_yaml_from(args.defaults),
                                    overrides=parsed_yaml_from(args.overrides))

    # Add the warrantee sticker
    print('The output assumes you have been pruning your old overrides '
          'files as needed and as suggested by release notes.')
    if any(key in ['NEW_DEFAULTS', 'OLD_OVERRIDES'] for
           key in returned_combined):
        if args.testing:
            for key in returned_combined['NEW_DEFAULTS'].keys():
                returned_combined[key] = returned_combined['NEW_DEFAULTS'][key]
            del returned_combined['NEW_DEFAULTS']
            del returned_combined['OLD_OVERRIDES']
        else:
            print('\nYour output has conflicts, examine it to make sure '
                  'values are as you wish them to be, check "NEW_DEFAULTS" and'
                  ' "OLD_OVERRIDES" specifically as you may or may not need '
                  'you\'re overrides as they are.')

    if os.path.isfile(args.output_file):
        raise SystemExit('The file you are creating already exists, '
                         'please move it, we will not overwrite the file.')
    with open(args.output_file, 'w') as fh:
        fh.write(yaml.safe_dump(returned_combined,
                                default_flow_style=False,
                                explicit_start=True))


if __name__ == '__main__':
    main()
