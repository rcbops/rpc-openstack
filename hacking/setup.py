#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.
import setuptools

version = '1.0.0'

setuptools.setup(
    name='rpco-hacking-checks',
    author='Rackspace Private Cloud',
    description='Hacking/Flake8 checks for rpc-openstack',
    version=version,
    install_requires=['hacking'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
    ],
    py_modules=['rpco_checks'],
    provides=['rpco_checks'],
    entry_points={
        'flake8.extension': [
            'rpco.git_title_bug = rpco_checks:OnceGitCheckCommitTitleBug',
            ('rpco.git_title_length = '
             'rpco_checks:OnceGitCheckCommitTitleLength'),
            ('rpco.git_title_period = '
             'rpco_checks:OnceGitCheckCommitTitlePeriodEnding'),
        ]
    },
)
