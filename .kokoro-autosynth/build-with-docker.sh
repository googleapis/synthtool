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

docker run \
    --env AUTOSYNTH_MULTIPLE_COMMITS=${AUTOSYNTH_MULTIPLE_COMMITS} \
    --env AUTOSYNTH_MULTIPLE_PRS=${AUTOSYNTH_MULTIPLE_PRS} \
    --env KOKORO_ARTIFACTS_DIR=/kokoro/artifacts \
    --env KOKORO_KEYSTORE_DIR=/kokoro/keystore \
    --env MULTISYNTH_CONFIG=${MULTISYNTH_CONFIG} \
    --env MULTISYNTH_SHARD=${MULTISYNTH_SHARD} \
    --env SYNTHTOOL_TRACK_OBSOLETE_FILES=${SYNTHTOOL_TRACK_OBSOLETE_FILES} \
    -v ${KOKORO_ARTIFACTS_DIR}:/kokoro/artifacts \
    -v ${KOKORO_KEYSTORE_DIR}:/kokoro/keystore \
    -it synthtool /synthtool/autosynth/docker/autosynth.sh
