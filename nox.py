# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import nox


@nox.session
def test(session):
    session.interpreter = 'python3.6'
    session.install('pytest')
    session.run('pip', 'install', '-e', '.')
    session.run('pytest', 'tests', *session.posargs)


@nox.session
def blacken(session):
    session.interpreter = 'python3.6'
    session.install('black')
    session.run('black', 'synthtool', 'tests')


@nox.session
def lint(session):
    session.interpreter = 'python3.6'
    session.install('mypy', 'flake8', 'black')
    session.run('pip', 'install', '-e', '.')
    session.run('black', '--check', 'synthtool', 'tests')
    session.run('flake8', 'synthtool', 'tests')
    session.run('mypy', '--ignore-missing-imports', 'synthtool')
