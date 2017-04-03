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

import argparse
import datetime
import errno
import os
import re
import sys
import yaml
import logging

import github3
import sh
from sh import git, awk

RELEASE_FILES = [
    'rpcd/playbooks/group_vars/all.yml',
    'rpcd/etc/openstack_deploy/user_rpco_variables_defaults.yml'
]


class Repo(object):
    def __init__(self, url='', cache_dir='', bare=False):
        valid_url = re.match(
            r'(?P<url>^ssh://git@github.com/(?P<owner>[a-zA-Z0-9-]+)/'
            r'(?P<name>[a-zA-Z0-9-]+).git$)',
            url
        )
        if not valid_url:
            raise ValueError('"%s" is not a valid URL.' % url)

        self.url = valid_url.group('url')
        self.owner = valid_url.group('owner')
        self.name = valid_url.group('name')
        self.cache_dir = os.path.expanduser(cache_dir)
        self.bare = bare
        self.dir = self.bare and '%s.git' % self.name or self.name
        self.path = os.path.join(self.cache_dir, self.dir)
        self.git = sh.git.bake(_cwd=self.path)

        try:
            self.remote = self._get_remote()
        except OSError as e:
            if e.errno == errno.ENOENT:
                self.remote = 'origin'
            else:
                raise e

        self._configure_repo()

        self.tags = self._get_tags()

    def _get_remote(self):
        remote_output = self.git.remote(verbose=True).stdout
        for line in remote_output.splitlines():
            name, rest = line.split('\t')
            if rest.startswith(self.url):
                break
        else:
            name = self.owner
            self.git.remote.add(name, self.url)

        return name

    def _configure_repo(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        if not os.path.exists(self.path):
            sh.git.clone(
                self.url, self.dir, _cwd=self.cache_dir, bare=self.bare
            )
        if self.bare:
            self.git.fetch(
                self.remote, '+refs/heads/*:refs/heads/*', tags=True
            )
        else:
            self.git.fetch()

    def _get_tags(self):
        all_tags = self.git.tag('-l')
        valid_tags = []
        for tag_str in all_tags:
            try:
                tag_obj = Tag(tag_str.strip(), repo=self)
            except ValueError:
                continue
            else:
                valid_tags.append(tag_obj)

        valid_tags.sort()
        return valid_tags

    def create_tag(self, tag_str=None, major=None, minor=None, patch=None,
                   rc=None, commit=None, message=None):
        tag = Tag(tag_str=tag_str, major=major, minor=minor, patch=patch,
                  rc=rc, repo=self)
        self.git.tag(tag, commit, a=True, m=message)
        self.git.push(self.remote, tag)
        self.tags.append(tag)
        self.tags.sort()
        return tag


class Tag(object):
    """rpc-openstack Git repository tag object."""

    def __init__(self, tag_str=None, major=None, minor=None, patch=None,
                 rc=None, repo=None):
        validate_tag = re.compile(
            r'^r(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)'
            r'(rc(?P<rc>[1-9][0-9]*))?$'
        )
        if tag_str:
            valid_tag = validate_tag.match(tag_str)
            if not valid_tag:
                raise ValueError('%s is not a valid tag.' % tag_str)
            _major = valid_tag.group('major')
            _minor = valid_tag.group('minor')
            _patch = valid_tag.group('patch')
            _rc = valid_tag.group('rc')
        elif None not in (major, minor, patch):
            _major = major
            _minor = minor
            _patch = patch
            _rc = rc
        else:
            raise ValueError('Insufficient data to construct tag.')

        self.major = int(_major)
        self.minor = int(_minor)
        self.patch = int(_patch)
        self.rc = _rc and int(_rc)
        self.rc_for = self.rc and 'r%s.%s.%s' % (_major, _minor, _patch)
        self.repo = repo

    def __repr__(self):
        tag_str = 'r%s.%s.%s' % (self.major, self.minor, self.patch)

        if self.rc:
            return '%src%s' % (tag_str, self.rc)
        else:
            return tag_str

    def __lt__(self, other):
        both_rc = all((self.rc, other.rc))
        self_rc = (both_rc and self.rc) or (not bool(self.rc))
        other_rc = (both_rc and other.rc) or (not bool(other.rc))

        return ((self.major, self.minor, self.patch, self_rc) <
                (other.major, other.minor, other.patch, other_rc))

    def __le__(self, other):
        return self < other or self == other

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return self > other or self == other

    @property
    def previous(self):
        """Return the previous tag.

        Determine the previous tag based on version numbers and return it. If
        self is not a release candidate tag the previous tag cannot be either.
        The previous tag does not examine the tags' timestamps and so the
        previous tag returned may have been created after self.
        :returns: :class: `__main__.Tag`, None
        """
        for tag in reversed(self.repo.tags):
            if tag >= self:
                continue
            elif tag.rc and not self.rc:
                continue
            else:
                previous = tag
                break
        else:
            previous = None

        return previous

    @property
    def next_revision(self):
        """Return the next revision tag.

        Calculate the next tag. The returned tag will be either the next patch
        tag or the next release candidate tag depending on whether or not self
        is release candidate.

        The returned tag object is not associated with a repo to prevent it
        from being mistaken for an actual Git tag on the repo.
        :returns: :class: `__main__.Tag`, None
        """
        if self.rc:
            patch = self.patch
            rc = self.rc + 1
        else:
            patch = self.patch + 1
            rc = self.rc

        return Tag(major=self.major, minor=self.minor, patch=patch, rc=rc)


class Release(object):
    def __init__(self, tag, github_token=None):
        self.tag = tag
        self.repo = tag.repo
        self.github_token = github_token
        self.gh = self._get_github_session()
        self.release_date = datetime.datetime.today()
        self.next_release_date = self._calculate_next_due_date()
        self.pre_release = bool(self.tag.rc)
        self.diff = self._generate_release_diff()

    def _get_github_session(self):
        gh = github3.GitHub(token=self.github_token)
        return gh.repository(self.repo.owner, self.repo.name)

    def _calculate_next_due_date(self):
        return self.release_date + datetime.timedelta(days=14)

    def _generate_release_diff(self):
        logging.warning("Generating release diff...")
        diff = sh.rpc_differ(self.tag.previous,
                             self.tag,
                             "--rpc-repo-url", self.repo.url,
                             update=True
                             ).stdout
        return sh.pandoc(
            '--from', 'rst',
            '--to', 'markdown_github',
            _in=diff
        ).stdout

    def publish_release(self):
        """Create GitHub release page for tag"""
        try:
            self.gh.create_release(tag_name=str(self.tag),
                                   name='Release %s' % self.tag,
                                   body=self.diff,
                                   prerelease=self.pre_release)
        except github3.exceptions.UnprocessableEntity:
            existing_release = self.gh.release_from_tag(str(self.tag))
            if existing_release:
                raise Exception(
                    'There is an existing release called %s.' % self.tag
                )
            else:
                raise

    def update_milestones(self, next_version=None):
        """Create GitHub milestone for next tag"""
        if not next_version:
            next_version = self.tag.next_revision
        try:
            milestone_rc = self.gh.create_milestone(
                title=str(next_version),
                due_on=self.next_release_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            )
        except github3.exceptions.UnprocessableEntity:
            next_milestone = None
            for milestone in self.gh.milestones():
                if milestone.title == next_version:
                    next_milestone = milestone
                    break
            if next_milestone:
                raise Exception(
                    'There is an existing milestone called %s.' % self.tag
                )
            else:
                raise
        else:
            if not milestone_rc:
                raise Exception(
                    'None object Returned (Probably a 404 due to auth issues)',
                    'cannot create milestone'
                )
        for milestone in self.gh.milestones():
            if milestone.title == self.tag:
                milestone.update(state='closed')
                break


def chk_devel_version(repo, branch, expected_release):
    repo.git.checkout(branch)
    repo.git.pull(repo.remote, branch)
    for release_file in RELEASE_FILES:
        filename = os.path.join(repo.path, release_file)
        with open(filename, 'r') as f:
            content = f.read()
        current_release = yaml.load(content)['rpc_release']
        version_check = os.getenv('RPC_VERSION_CHECK', True)
        if (current_release != expected_release and
                version_check not in ['False', 'no', 'FALSE', 'NO']):
            raise Exception('{} in {} does not match expected version {}'
                            .format(current_release, filename,
                                    expected_release))


def update_repo_with_new_ver_number(repo, branch, new_version_number):
    ''' Update the future_tag into repo, then git add, commit and push.
    '''

    repo.git.checkout(branch)
    repo.git.pull(repo.remote, branch)
    for release_file in RELEASE_FILES:
        filename = os.path.join(repo.path, release_file)
        with open(filename, 'r') as release_fh:
            lines = release_fh.readlines()
        with open(filename, 'w') as f:
            for line in lines:
                f.write(re.sub(r'rpc_release(: |=).*$',
                               r"rpc_release\1" + new_version_number,
                               line))
        repo.git.add(filename)

    msg_title = 'Start {} dev cycle'.format(new_version_number)
    msg_body = 'This is an automatic commit.'
    repo.git.commit(m='%s\n\n%s' % (msg_title, msg_body))
    repo.git.push(repo.remote, branch)


def request_doc_update(github_token, repo, release):
    gh = github3.GitHub(token=github_token)
    gh_repo = gh.repository(repo.owner, repo.name)
    issue_title = 'RPCO Release %s' % release.tag
    issue_body = (
        'Update release notes and documentation history.\n\n'
        'This new RPCO release is now available to be deployed on customer'
        ' environments. [Release notes can be viewed on GitHub] [1]\n'
        '[1]: https://github.com/rcbops/rpc-openstack/releases/tag/%s'
    ) % release.tag
    issue = gh_repo.create_issue(title=issue_title, body=issue_body)
    major = release.tag.major
    try:
        repo.git('rev-parse', '--verify', '%s/v%s' % (repo.remote, major + 1))
    except sh.ErrorReturnCode_128:
        from_branch = 'issues/%s/master' % issue.number
        to_branch = 'master'
        cherrypick = {'from_branch': 'issues/%s/v%s' % (issue.number, major),
                      'to_branch': 'v%s' % major}
    else:
        from_branch = 'issues/%s/v%s' % (issue.number, major)
        to_branch = 'v%s' % major
        cherrypick = None
    repo.git.checkout('%s/%s' % (repo.remote, to_branch), b=from_branch)
    overview_file = os.path.join(repo.path, 'common/overview-dochistory.rst')

    with open(overview_file) as fo_r:
        overview_data = fo_r.readlines()

    overview_addition = (
        '   * - %s\n     - Rackspace Private Cloud %s release\n' %
        (release.release_date.strftime('%Y-%m-%d'), release.tag)
    )
    with open(overview_file, 'w') as fo_w:
        for num, line in enumerate(overview_data):
            fo_w.write(line)
            if line.strip() == '- Release information':
                fo_w.write(overview_addition)
                break
        else:
            raise Exception('"%s" does not match expected format.' %
                            overview_file)
        fo_w.writelines(overview_data[num + 1:])

    repo.git.add(overview_file)

    if major == 11:
        whats_new_file = os.path.join(
            repo.path, 'doc/rpc-releasenotes/whats-new-v%s-1.rst' % major
        )
    else:
        whats_new_file = os.path.join(
            repo.path, 'doc/rpc-releasenotes/whats-new-v%s.rst' % major
        )

    with open(whats_new_file) as fn_r:
        whats_new_data = fn_r.readlines()

    whats_new_addition = (
        '\n- For detailed changes in RPCO %(tag)s, see'
        '\n  `github.com/rcbops/rpc-openstack/releases/tag/%(tag)s'
        '\n  <https://github.com/rcbops/rpc-openstack/releases/tag/%(tag)s>`_.'
        '\n\n  - This is a maintenance release.\n'
    ) % {'tag': release.tag}

    whats_new_addition_12 = (
        '\n  * For detailed changes in rpc-openstack release %(tag)s, see'
        '\n    `github.com/rcbops/rpc-openstack/releases/tag/%(tag)s\n'
        '      <https://github.com/rcbops/rpc-openstack/releases/tag/%(tag)s>`'
        '_.\n\n    - %(tag)s includes fixes for several bugs\n'
    ) % {'tag': release.tag}

    whats_new_addition_11 = (
        '\n- To see detailed changes in the RPCO'
        '\n  `%(tag)s <https://github.com/rcbops/rpc-openstack/releases/tag/'
        '%(tag)s>`_'
        '\n  release, click the `%(prev)s...%(tag)s change'
        '\n  log <https://github.com/rcbops/rpc-openstack/compare/'
        '%(prev)s...%(tag)s>`_.\n'
    ) % {'tag': release.tag, 'prev': release.tag.previous}

    with open(whats_new_file, 'w') as fn_w:
        for num, line in enumerate(whats_new_data):
            fn_w.write(line)
            if major == 12 and set(line.strip()) == {'~'}:
                fn_w.write(whats_new_addition_12)
                break
            elif major == 11 and line.strip() == '**Changes per release**':
                fn_w.write(whats_new_addition_11)
                break
            elif major not in (11, 12) and set(line.strip()) == {'~'}:
                fn_w.write(whats_new_addition)
                break
        else:
            raise Exception('"%s" does not match expected format.' %
                            whats_new_file)
        fn_w.writelines(whats_new_data[num + 1:])

    repo.git.add(whats_new_file)

    msg_title = 'Add release %s to documentation' % release.tag
    msg_body = 'Issue: %s' % issue.html_url
    repo.git.commit(m='%s\n\n%s' % (msg_title, msg_body))
    repo.git.push(repo.remote, from_branch)
    gh_repo.create_pull(title=msg_title, body=msg_body, base=to_branch,
                        head=from_branch)

    if cherrypick:
        repo.git.checkout('%s/%s' % (repo.remote, cherrypick['to_branch']),
                          b=cherrypick['from_branch'])
        repo.git('cherry-pick', from_branch, x=True)
        repo.git.push(repo.remote, cherrypick['from_branch'])
        gh_repo.create_pull(title=msg_title,
                            body=msg_body,
                            base=cherrypick['to_branch'],
                            head=cherrypick['from_branch'])


def build_parser():
    parser = argparse.ArgumentParser(description='Publish RPCO tag.')
    parser.add_argument(
        '--cache-dir', help='Directory where cached data will be stored.',
        type=os.path.expanduser, default='~/.rpco-release-tool',
    )
    parser.add_argument(
        '--repo-url', help='URL of repo to update.',
        default='ssh://git@github.com/rcbops/rpc-openstack.git',
    )
    parser.add_argument(
        '--docs-repo-url', help='URL of docs repo to update.',
        default='ssh://git@github.com/rackerlabs/docs-rpc.git',
    )
    parser.add_argument(
        '--branch', help='Branch to update'
    )
    parser.add_argument(
        '--tag', type=Tag, required=True, help='Name of new tag.'
    )
    parser.add_argument(
        '--future-tag', type=Tag,
        help='The version number for the next cycle'
    )
    parser.add_argument(
        '--do-not-publish-release', default=False, action='store_true',
        help='Do not publish a github release for this release'
    )
    parser.add_argument(
        '--do-not-update-milestones', default=False, action='store_true',
        help='Do not update github milestones'
    )
    parser.add_argument(
        '--do-not-file-docs-issue', default=False, action='store_true',
        help='Do not create a docs issue for this release'
    )
    parser.add_argument(
        '--do-not-change-files-with-release-version', default=False,
        action='store_true',
        help='Do not update files with the new rpc_release: "future tag"'
    )
    existing = parser.add_mutually_exclusive_group(required=True)
    existing.add_argument(
        '--commit', help='Reference to the commit to tag.'
    )
    existing.add_argument(
        '--existing-release', default=False, action='store_true'
    )
    parser.add_argument('--github-token')
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.branch:
        branch = str(args.branch)
    else:
        # Discover branch from current repository
        try:
            branch = str(
                    awk(
                        git("branch", "--no-color"),
                        "/*/ { print $2; } ")
                ).strip()
        except:
            return "The current branch cannot be discovered."

    proceed_text = (
        'WARNING - Running this script will:\n'
        '  - add a tag to %s\n'
        '  - update branch %s with new version number\n'
        '  - submit an issue/pull-request to %s\n'
        'If you still wish to proceed type "YES": '
    ) % (args.repo_url, branch,  args.docs_repo_url)

    proceed = raw_input(proceed_text)

    if proceed != 'YES':
        return

    if args.github_token:
        token = args.github_token
    elif os.environ.get('RPC_GITHUB_TOKEN', False):
        token = os.environ['RPC_GITHUB_TOKEN']
    else:
        return "Token neither found in the CLI nor in env vars"

    # Instantiate a repo.
    # Do not use bare repo because changes has to be pushed into it.
    # If you had a bare repo present in your cache dir, please delete it.
    rpco_repo = Repo(url=args.repo_url, cache_dir=args.cache_dir, bare=False)

    # Ensure the proper version of the tag before attempting to release it
    chk_devel_version(rpco_repo, branch, str(args.tag))

    if args.existing_release:
        rpco_tag = rpco_repo.tags[rpco_repo.tags.index(args.tag)]
    else:
        tag_message = 'Release %s' % args.tag
        rpco_tag = rpco_repo.create_tag(
            tag_str=str(args.tag), commit=args.commit, message=tag_message
        )
    release = Release(rpco_tag, github_token=token)

    if not args.future_tag:
        future_tag = release.tag.next_revision()
    else:
        future_tag = args.future_tag

    if not args.existing_release:
        if not args.do_not_publish_release:
            logging.warning("Publishing github release...")
            release.publish_release()
        if not args.do_not_update_milestones:
            logging.warning("Updating github milestones...")
            release.update_milestones(next_version=future_tag)

    if (not args.do_not_file_docs_issue and
            not release.pre_release):
        docs_repo = Repo(url=args.docs_repo_url, cache_dir=args.cache_dir,
                         bare=False)
        request_doc_update(token, docs_repo, release)

    if not args.do_not_change_files_with_release_version:
        logging.warning("The new dev cycle for branch {} will be: {}"
                        .format(branch, str(future_tag)))
        update_repo_with_new_ver_number(rpco_repo, branch,
                                        str(future_tag))

if __name__ == '__main__':
    sys.exit(main())
