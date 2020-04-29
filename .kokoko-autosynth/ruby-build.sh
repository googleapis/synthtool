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

cd ${KOKORO_ARTIFACTS_DIR}/git/autosynth

# Download yarn public key
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -

# Upgrade the NPM version
sudo npm install -g npm

# Install bazel 1.2.0
mkdir -p ~/bazel
curl -L https://github.com/bazelbuild/bazel/releases/download/1.2.0/bazel-1.2.0-linux-x86_64 -o ~/bazel/bazel
chmod +x ~/bazel/bazel
export PATH=~/bazel:"$PATH"

# Kokoro currently uses 3.6.1
pyenv global 3.6.1

# Disable buffering, so that the logs stream through.
export PYTHONUNBUFFERED=1

# Add github to known hosts.
ssh-keyscan github.com >> ~/.ssh/known_hosts

# Kokoro exposes this as a file, but the scripts expect just a plain variable.
export GITHUB_TOKEN=$(cat ${KOKORO_KEYSTORE_DIR}/73713_yoshi-automation-github-key)

# Setup git credentials
echo "https://${GITHUB_TOKEN}:@github.com" >> ~/.git-credentials
git config --global credential.helper 'store --file ~/.git-credentials'

# Install ruby
sudo apt-get update && sudo apt-get install -y git curl autoconf bison build-essential \
    libssl-dev libreadline-dev zlib1g-dev libyaml-dev ca-certificates

mkdir $HOME/.ruby
git clone https://github.com/rbenv/ruby-build.git $HOME/.ruby-build
$HOME/.ruby-build/bin/ruby-build 2.5.3 $HOME/.ruby
export PATH=$HOME/.ruby/bin:$PATH
gem install bundler:1.17.3 rake

# Run autosynth
python3 -m venv env
source env/bin/activate
python3 -m pip install --upgrade --quiet -r requirements.txt
python3 -m autosynth.multi --config ${MULTISYNTH_CONFIG}
