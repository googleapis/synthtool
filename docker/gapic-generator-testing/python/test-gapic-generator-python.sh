#!/bin/bash
# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Fail immediately.
set -e

# Reset local copy of googleapis-generated-clients
rm -rf googleapis-generated-clients
mkdir googleapis-generated-clients

# path to clone of https://github.com/googleapis/gapic-generator-python
export GAPIC_GENERATOR_PYTHON=${GAPIC_GENERATOR_PYTHON:=`realpath gapic-generator-python`}

# path to clone of https://github.com/googleapis/googleapis with
#   with the correct source branch checked out.
export GOOGLEAPIS=${GOOGLEAPIS:=`realpath googleapis`}

# path to empty directory for the generated clients
export GOOGLEAPIS_GEN=${GOOGLEAPIS_GEN:=`realpath googleapis-generated-clients`}

sed -i  '/_gapic_generator_python_version/,/)/c\
local_repository (\
    name = "gapic_generator_python",\
    path = "'$GAPIC_GENERATOR_PYTHON'"\
)' $GOOGLEAPIS/WORKSPACE

# Pull googleapis to make sure we're up to date.
git -C "$GOOGLEAPIS" pull

# python compute api only for now
targets="//google/cloud/compute/v1:compute-v1-py"

fetch_targets="$targets"

(cd "$GOOGLEAPIS" && bazel fetch $BAZEL_FLAGS $fetch_targets)

# Some API always fails to build.  One failing API should not prevent all other
# APIs from being updated.
set +e

# Invoke bazel build.
(cd "$GOOGLEAPIS" && bazel build $BAZEL_FLAGS -k $targets)

let target_count=0
failed_targets=()
for target in $targets ; do
    let target_count++
    tar_gz=$(echo "${target:2}.tar.gz" | tr ":" "/")
    # Create the parent directory if it doesn't already exist.
    parent_dir=$(dirname $tar_gz)
    target_dir="$GOOGLEAPIS_GEN/$parent_dir"
    mkdir -p "$target_dir"
    tar -xf "$GOOGLEAPIS/bazel-bin/$tar_gz" -C "$target_dir" || {
        failed_targets+=($target)
        # Restore the original source code because bazel failed to generate
        # the new source code.
        git -C "$GOOGLEAPIS_GEN" checkout -- "$target_dir"
        # TODO: report an issue with 'gh'
    }
done

# Report build failures.
let failed_percent="100 * ${#failed_targets[@]} / $target_count"
set -e
echo "$failed_percent% of targets failed to build."
printf '%s\n' "${failed_targets[@]}"

# Loop through all generated clients

# Run unit tests for a specific python version for all `google.*` clients
noxfiles=$(find "googleapis-generated-clients/google" -name "noxfile.py")

for noxfile in $noxfiles ; do
    noxfile_parent_dir=$(dirname $noxfile)
    cd $noxfile_parent_dir && nox -s unit-3.8
done

# Report unit test failures
