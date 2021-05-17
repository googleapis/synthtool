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

# Upgrade the NPM version
sudo npm install -g npm

# Install bazel 3.0.0
mkdir -p ~/bazel
curl -L https://github.com/bazelbuild/bazel/releases/download/4.0.0/bazel-4.0.0-linux-x86_64 -o ~/bazel/bazel
chmod +x ~/bazel/bazel
export PATH=~/bazel:"$PATH"

# Kokoro currently uses 3.6.1, but upgrade to 3.6.9 as virtualenv creation
# is broken in 3.6.1 with virtualenv>=20.0.0
# Also, see b/187701234 for an explanation of 783870759566a77d09b426e0305bc0993a522765
cd /home/kbuilder/.pyenv/plugins/python-build/../.. \
    && git pull \
    && git checkout 783870759566a77d09b426e0305bc0993a522765 \
    && cd -

pyenv install 3.6.9
pyenv global 3.6.9

# use python installed by pyenv and use python3.6 specific set of dependencies
echo "build --extra_toolchains=@gapic_generator_python//:pyenv3_toolchain --define=gapic_gen_python=3.6" > $HOME/.bazelrc
echo "test --extra_toolchains=@gapic_generator_python//:pyenv3_toolchain --define=gapic_gen_python=3.6" >> $HOME/.bazelrc

# Disable buffering, so that the logs stream through.
export PYTHONUNBUFFERED=1

# Add github to known hosts.
ssh-keyscan github.com >> ~/.ssh/known_hosts

# Kokoro exposes this as a file, but the scripts expect just a plain variable.
export GITHUB_TOKEN=$(cat ${KOKORO_KEYSTORE_DIR}/73713_yoshi-automation-github-key)

# Setup git credentials
echo "https://${GITHUB_TOKEN}:@github.com" >> ~/.git-credentials
git config --global credential.helper 'store --file ~/.git-credentials'

python3 -m venv env
source env/bin/activate
python3 -m pip install --upgrade --quiet -r requirements.txt
export PYTHONPATH=`pwd`
python3 -m autosynth.multi --config ${MULTISYNTH_CONFIG}
