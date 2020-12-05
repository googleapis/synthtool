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

# Install bazel 3.0.0
mkdir -p ~/bazel
curl -L https://github.com/bazelbuild/bazel/releases/download/3.0.0/bazel-3.0.0-linux-x86_64 -o ~/bazel/bazel
chmod +x ~/bazel/bazel
export PATH=~/bazel:"$PATH"

# Install synthtool GAPIC Bazel dependencies
sudo apt-get update
sudo apt-get install -y --no-install-recommends zip unzip

# Bazel expects python3 at /usr/bin/python
sudo ln -s /usr/bin/python3.8 /usr/bin/python

# Disable buffering, so that the logs stream through.
export PYTHONUNBUFFERED=1

# Kokoro exposes this as a file, but the scripts expect just a plain variable.
export GITHUB_TOKEN=$(cat ${KOKORO_KEYSTORE_DIR}/73713_yoshi-automation-github-key)

# Setup git credentials
echo "https://${GITHUB_TOKEN}:@github.com" >> ~/.git-credentials
git config --global credential.helper 'store --file ~/.git-credentials'

# Run autosynth
python3 -m venv env
source env/bin/activate
python3 -m pip install --upgrade --quiet -r requirements.txt
export PYTHONPATH=`pwd`
python3 -m autosynth.multi --config ${MULTISYNTH_CONFIG}
