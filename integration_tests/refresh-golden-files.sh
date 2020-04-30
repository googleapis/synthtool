# Copyright 2020 Google LLC
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

# Until we can lock sources (github repos, docker images, etc.) to fixed
# version numbers, the output of generation will change frequently, and the
# integration tests will fail.
#
# Run this script *in*a*clean*branch* to refresh all the golden files.
python -m pytest | grep -o -e "cp /tmp/.*" | bash