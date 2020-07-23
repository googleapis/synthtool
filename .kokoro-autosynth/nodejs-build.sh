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

# Ensure `curl` is available
sudo apt-get update && sudo apt-get -y install curl

# Use `nvm` to bootstrap the installation of node.js and npm.
# To learn more: https://github.com/nvm-sh/nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash

# Activate `nvm` so the binary is available on the path
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Use the latest LTS version of nodejs.  This can change over time, but
# should prevent the need to modify this file every year.
nvm install --lts

# Verify expected versions of nodejs and npm
node --version
npm --version

# Run the normal autosynth build
${KOKORO_ARTIFACTS_DIR}/github/synthtool/.kokoro-autosynth/build.sh
