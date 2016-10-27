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

import mock
import os.path
import unittest

from release import Repo, Tag

import release


class TestTagMethods(unittest.TestCase):
    def test_tag_str(self):
        tag_strings = ('r1.2.3', 'r1.2.3rc1', 'r1.2.3rc1')
        for tag_string in tag_strings:
            tag = Tag(tag_string)
            self.assertEqual(tag_string, str(tag))

    def test_tag_initialisation_equivalence(self):
        tags = (
            ('r1.2.3', '1', '2', '3', None),
            ('r1.2.3rc1', '1', '2', '3', '1'),
        )
        for tag_string, major, minor, patch, rc in tags:
            tag_from_string = Tag(tag_string)
            tag_from_parts = Tag(major=major, minor=minor, patch=patch, rc=rc)
            self.assertEqual(tag_from_string, tag_from_parts)

    def test_tag_initialisation_failures(self):
        bad_tags = ('1.2.3', 'v1.2.3', 'r1.2.3rc0', 'r1.2')

        for tag in bad_tags:
            self.assertRaises(ValueError, Tag, tag)

    def test_tag_comparison(self):
        tags_different = (
            ('r1.0.0rc1', 'r1.0.0rc2'),
            ('r1.0.0rc2', 'r1.0.0'),
            ('r1.0.0', 'r1.0.1'),
            ('r1.0.0', 'r1.1.0'),
            ('r1.0.0', 'r2.0.0rc1'),
            ('r1.0.0', 'r2.0.0'),
            ('r2.0.0', 'r10.0.0'),
            ('r1.2.0', 'r1.10.0'),
            ('r1.0.2', 'r1.0.10'),
            ('r1.0.0rc2', 'r1.0.0rc10'),
        )

        for smaller, bigger in tags_different:
            self.assertLess(Tag(smaller), Tag(bigger))
            self.assertLessEqual(Tag(smaller), Tag(bigger))
            self.assertGreater(Tag(bigger), Tag(smaller))
            self.assertGreaterEqual(Tag(bigger), Tag(smaller))
            self.assertNotEqual(Tag(bigger), Tag(smaller))

        tag_strings = ('r1.2.3', 'r1.2.3rc1')
        for tag in tag_strings:
            self.assertEqual(Tag(tag), Tag(tag))
            self.assertLessEqual(Tag(tag), Tag(tag))
            self.assertGreaterEqual(Tag(tag), Tag(tag))

    def test_previous(self):
        tag_string_pairs = (
            ('r1.0.0rc1', None),
            ('r1.0.0rc2', 'r1.0.0rc1'),
            ('r1.0.0', None),
            ('r2.0.0rc1', 'r1.0.0'),
            ('r2.0.0', 'r1.0.0'),
            ('r2.0.1', 'r2.0.0')
        )
        tags = []
        repo = mock.Mock(tags=tags)
        tag_pairs = []
        for current, previous in tag_string_pairs:
            current_tag = Tag(current, repo=repo)
            previous_tag = previous and Tag(previous, repo=repo)

            tags.append(current_tag)
            previous_tag and tags.append(previous_tag)

            tag_pairs.append((current_tag, previous_tag))

        tags.sort()

        for tag, previous in tag_pairs:
            self.assertEqual(tag.previous, previous)

    def test_next_revision(self):
        tag_string_pairs = (
            ('r1.0.0rc1', 'r1.0.0rc2'),
            ('r1.0.0', 'r1.0.1'),
            ('r2.3.4', 'r2.3.5'),
        )

        for tag, next_tag in tag_string_pairs:
            self.assertEqual(Tag(tag).next_revision, Tag(next_tag))


class TestRepoMethods(unittest.TestCase):
    def setUp(self):
        release.sh.git = mock.Mock()
        self.git = release.sh.git.bake()
        release.os.makedirs = mock.Mock()
        release.os.path.exists = mock.Mock(return_value=True)
        release.os.path.expandsuser = mock.Mock(side_effect=lambda x: x)

    def test_repo_url_validation(self):
        remote = 'origin'
        Repo._get_remote = mock.Mock(return_value=remote)
        Repo._configure_repo = mock.Mock()
        Repo._get_tags = mock.Mock()
        valid_urls = (
            'ssh://git@github.com/testowner/testrepo.git',
        )
        invalid_urls = (
            '',
            'https://github.com/testowner/testrepo.git',
        )
        for valid_url in valid_urls:
            repo = Repo(valid_url)
            self.assertEqual(repo.url, valid_url)

        for invalid_url in invalid_urls:
            self.assertRaises(ValueError, Repo, invalid_url)

    def test_repo_defaults(self):
        remote = 'origin'
        Repo._get_remote = mock.Mock(return_value=remote)
        Repo._configure_repo = mock.Mock()
        tags = mock.Mock()
        Repo._get_tags = mock.Mock(return_value=tags)
        owner = 'testowner'
        name = 'testrepo'
        cache_dir = ''
        url = 'ssh://git@github.com/%s/%s.git' % (owner, name)

        attributes = {
            'url': url,
            'owner': owner,
            'name': name,
            'cache_dir': cache_dir,
            'bare': False,
            'dir': name,
            'path': name,
            'git': self.git,
            'tags': tags,
        }
        repo = Repo(url)

        for attribute, value in attributes.items():
            self.assertEqual(getattr(repo, attribute), value)

    def test_repo_overrides(self):
        remote = 'origin'
        Repo._get_remote = mock.Mock(return_value=remote)
        Repo._configure_repo = mock.Mock()
        tags = mock.Mock()
        Repo._get_tags = mock.Mock(return_value=tags)
        owner = 'testowner'
        name = 'testrepo'
        cache_dir = 'testcachedir'
        directory = '%s.git' % name
        url = 'ssh://git@github.com/%s/%s.git' % (owner, name)
        bare = True

        attributes = {
            'url': url,
            'owner': owner,
            'name': name,
            'cache_dir': cache_dir,
            'bare': bare,
            'dir': directory,
            'path': os.path.join(cache_dir, directory),
            'git': self.git,
            'tags': tags,
        }
        repo = Repo(url, cache_dir=cache_dir, bare=bare)

        for attribute, value in attributes.items():
            self.assertEqual(getattr(repo, attribute), value)

    def test_create_tag(self):
        remote = 'origin'
        Repo._get_remote = mock.Mock(return_value=remote)
        Repo._configure_repo = mock.Mock()
        tags = [Tag('r1.0.0'), Tag('r1.5.0')]
        Repo._get_tags = mock.Mock(return_value=tags)

        owner = 'testowner'
        name = 'testrepo'
        url = 'ssh://git@github.com/%s/%s.git' % (owner, name)

        repo = Repo(url)

        tag_str = 'r1.2.3'
        commit = 'commit'
        message = 'Test tag.'
        tag = repo.create_tag(tag_str, commit=commit, message=message)

        self.git.tag.assert_called_once_with(tag, commit, a=True, m=message)
        self.git.push.assert_called_once_with(remote, tag)
        self.assertIn(tag, repo.tags)
        self.assertEqual(repo.tags.index(tag), 1)
