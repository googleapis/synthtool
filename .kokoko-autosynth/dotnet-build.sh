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

export DOTNET_SKIP_FIRST_TIME_EXPERIENCE=true
export DOTNET_CLI_TELEMETRY_OPTOUT=true

# Install .NET Core, working around an installation issue. See:
# - https://github.com/dotnet/core-setup/issues/4049
# - https://stackoverflow.com/questions/54065894
curl -s https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
sudo mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg
sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-xenial-prod xenial main" > /etc/apt/sources.list.d/dotnetdev.list'

sudo apt-get -qq install -y apt-transport-https
sudo apt-get -qq update
sudo apt-get -qq install -y dotnet-sdk-2.2=2.2.105-1
sudo apt-get -qq install -y dotnet-sdk-3.1=3.1.102-1

# Run the normal autosynth build
${KOKORO_ARTIFACTS_DIR}/git/synthtool/.kokoro-autosynth/build.sh
