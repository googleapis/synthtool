#!/bin/bash
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -eo pipefail

cd ${KOKORO_ARTIFACTS_DIR}/github/synthtool

# Install more versions of Python so repo owners can choosoe which version
# of Python to run the formatter 'black' with
cd /home/kbuilder/.pyenv/plugins/python-build/../.. && git pull && cd -
pyenv install 3.6.10
pyenv install 3.7.7
pyenv install 3.8.3

# 'pyenv shell' takes precedence over 'pyenv global'
pyenv shell 3.6.10 3.7.7 3.8.3

# Run the normal autosynth build
${KOKORO_ARTIFACTS_DIR}/github/synthtool/.kokoro-autosynth/build.sh