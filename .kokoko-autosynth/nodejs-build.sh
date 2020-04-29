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

cd ${KOKORO_ARTIFACTS_DIR}/git/synthtool

# Install Node 12, as the Kokoro image
# uses an older version by default
curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
sudo apt-get install -y nodejs

sudo rm /usr/local/bin/node
sudo ln -s /usr/bin/nodejs /usr/local/bin/node

# Verify Node 12 is being used
node --version

# Run the normal autosynth build
${KOKORO_ARTIFACTS_DIR}/git/synthtool/.kokoro-autosynth/build.sh
