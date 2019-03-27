#!/bin/bash

# Copyright 2019 Google LLC
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

VERSION=$(npm view {{ metadata['repo']['distribution_name'] }} version)

python3 -m docuploader create-metadata \
			--name {{ metadata['repo']['name'] }} \
			--version ${VERSION} \
			--language {{ metadata['repo']['language'] }} \
			--distribution-name {{ metadata['repo']['name'] }} \
			--github-repository https://github.com/{{ metadata['repo']['repo'] }} \
			--product-page {{ metadata['repo']['product_documentation']}} \
			--issue-tracker {{ metadata['repo']['issue_tracker'] }} \
			docs/docs.metadata

python3 -m docuploader upload docs
