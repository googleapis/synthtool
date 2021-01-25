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

@nox.session(python=['3.6'])
def generate_protos(session):
    session.install("grpcio-tools")
    session.run(
        "python", "-m", "grpc_tools.protoc", "-Isynthtool/protos", "--python_out=synthtool/protos", "synthtool/protos/metadata.proto", "synthtool/protos/preconfig.proto")

@nox.session(python=['3.6', '3.8'])
def blacken(session):
    session.install('black==19.10b0')
    session.run('black', 'synthtool', 'tests', 'autosynth', 'integration_tests')


@nox.session(python=['3.6', '3.8'])
def lint(session):
    session.install('mypy==0.790', 'flake8', 'black==19.10b0')
    session.run('pip', 'install', '-e', '.')
    session.run('black', '--check', 'synthtool', 'tests')
    session.run('flake8', 'synthtool', 'tests', 'autosynth', 'integration_tests')
    session.run('mypy', 'synthtool', 'autosynth')


@nox.session(python=['3.6', '3.8'])
def test(session):
    session.install('pytest', 'pytest-cov', 'requests_mock', 'watchdog')
    session.run('pip', 'install', '-e', '.')
    session.run('pytest', '--cov-report', 'term-missing', '--cov', 'autosynth', 'synthtool', 'tests', *session.posargs)