#!/bin/bash
# Copyright 2024 Google LLC
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

set -eo pipefail

python3 -m pip install keyring
python3 -m pip install keyrings.google-artifactregistry-auth

python3 -m keyring --list-backends

echo "[distutils]
index-servers =
    aoss-1p-python

[aoss-1p-python]
repository: https://us-python.pkg.dev/cloud-aoss-1p/cloud-aoss-1p-python/" >> $HOME/.pypirc

echo "[install]
index-url = https://us-python.pkg.dev/cloud-aoss-1p/cloud-aoss-1p-python/simple/
trusted-host = us-python.pkg.dev" >> $HOME/pip.conf

export PIP_CONFIG_FILE=$HOME/pip.conf

# Start the releasetool reporter
python3 -m pip install --require-hashes -r github/{{ metadata['repo']['repo'].split('/')[1] }}/.kokoro/requirements.txt
python3 -m releasetool publish-reporter-script > /tmp/publisher-script; source /tmp/publisher-script

# Disable buffering, so that the logs stream through.
export PYTHONUNBUFFERED=1

# Move into the package, build the distribution and upload.
TWINE_PASSWORD=$(cat "${KOKORO_KEYSTORE_DIR}/73713_google-cloud-pypi-token-keystore-1")
cd github/{{ metadata['repo']['repo'].split('/')[1] }}
python3 setup.py sdist bdist_wheel
twine upload --username __token__ --password "${TWINE_PASSWORD}" dist/*
