#!/bin/bash
# Copyright 2026 Google LLC
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

# File for local development of the Docker image. This is not intended to be used in CI, but can be used to test changes to the Dockerfile and entrypoint script.
set -e

# Get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
# Navigate to the root of the synthtool repo
cd "$DIR/../../.."

echo "Preparing post-processor-changes.txt..."
# Generate post-processor-changes.txt as expected by some Dockerfiles/CI
git log -1 --format="%B%n%nSource-Link: https://github.com/googleapis/synthtool/commit/%H" > post-processor-changes.txt && 
sed -i "s/([^()]*)$//g" post-processor-changes.txt && 
sed -i "s/^\(feat\|fix\)/chore/g" post-processor-changes.txt && 
sed -i "s/\!:/:/g" post-processor-changes.txt

echo "Building owlbot-nodejs-mono-repo..."
docker build -t owlbot-nodejs-mono-repo -f docker/owlbot/nodejs_mono_repo/Dockerfile .

# Cleanup temporary file
rm post-processor-changes.txt

echo ""
echo "Successfully built owlbot-nodejs-mono-repo"
echo "To run it against a local repository, use:"
echo "  docker run --rm -v \$(pwd):/workspace -w /workspace owlbot-nodejs-mono-repo [RELATIVE_DIRS]"
