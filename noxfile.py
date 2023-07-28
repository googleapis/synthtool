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

PYTHON_VERSIONS = ['3.8', '3.10']

# Error if a python version is missing
nox.options.error_on_missing_interpreters = True

@nox.session(python=PYTHON_VERSIONS)
def generate_protos(session):
    session.install("grpcio-tools")
    session.run(
        "python", "-m", "grpc_tools.protoc", "-Isynthtool/protos", "--python_out=synthtool/protos", "synthtool/protos/metadata.proto", "synthtool/protos/preconfig.proto")

@nox.session(python=PYTHON_VERSIONS)
def blacken(session):
    session.install('black==23.3.0', 'click>8.0')
    session.run('black', 'synthtool', 'tests')


@nox.session(python=PYTHON_VERSIONS)
def lint(session):
    session.install('mypy==0.790', 'flake8', 'black==23.3.0')
    session.run('pip', 'install', '-e', '.')
    session.run('pip', 'install', 'click>8.0')
    session.run('black', '--check', 'synthtool', 'tests')
    session.run('flake8', 'synthtool', 'tests')
    session.run('mypy', 'synthtool')


@nox.session(python=PYTHON_VERSIONS)
def test(session):
    session.install('pytest', 'pytest-cov', 'requests_mock', 'watchdog', 'flake8')
    session.run('pip', 'install', '-e', '.')
    session.run('pytest', '--cov-report', 'term-missing', '--cov', 'synthtool', 'tests', *session.posargs)
