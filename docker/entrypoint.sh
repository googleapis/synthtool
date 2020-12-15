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

# Bring npm and node into PATH.
source /root/.bashrc

cd /synthtool

# Disable buffering, so that the logs stream through.
export PYTHONUNBUFFERED=1

# Add github to known hosts.
mkdir -p ~/.ssh
ssh-keyscan github.com >> ~/.ssh/known_hosts

# Setup git credentials
echo "https://${GITHUB_TOKEN}:@github.com" >> ~/.git-credentials
git config --global credential.helper 'store --file ~/.git-credentials'

python -m autosynth.multi --config ${MULTISYNTH_CONFIG}
