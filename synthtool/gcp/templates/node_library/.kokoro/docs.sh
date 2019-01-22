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

set -xeo pipefail

export NPM_CONFIG_PREFIX=/home/node/.npm-global

cd $(dirname $0)/..

npm install

npm run docs

DOCS_LOCATION=./docs

if [ ! -d $DOCS_LOCATION ]; then
    echo "No docs generated, skipping link checker..";
    exit 0;
fi

# Check broken links
echo "Running link checker"
npm install broken-link-checker http-server
npx http-server -p 8080 $DOCS_LOCATION
npx blc http://localhost:8080 -r --exclude www.googleapis.com

