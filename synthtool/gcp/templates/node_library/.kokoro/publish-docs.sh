#!/bin/bash

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

set -eo pipefail

cd $(dirname $0)/..

npm install

npm run docs

# Publish documentation with docuploader.
python3 -m pip install --user gcp-docuploader

VERSION=$(npm view {{ metadata['name'] }} version)

# TODO(busunkim): Add product-page and issue-tracker
python3 -m docuploader create-metadata \
			--name {{ metadata['product'] }} \
			--version ${VERSION}\
			--language nodejs \
			--distribution-name {{ metadata['name'] }} \
			--github-repository https://github.com/{{ metadata['repository'] }} \
			docs/docs.metadata

python3 -m docuploader upload docs
