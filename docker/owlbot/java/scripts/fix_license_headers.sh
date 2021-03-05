#!/bin/bash
# Copyright 2021 Google LLC
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

set -e

last_commit_files=$(git diff-tree --no-commit-id -r $(git rev-parse HEAD) --name-only --diff-filter=M)
current_modified_files=$(git diff --name-only HEAD)
all_files=$(echo ${last_commit_files} ${current_modified_files} | sort -u)

for file in ${all_files}
do
  # if the header year changed in the last diff,
  # then restore the previous year
  old_copyright=$(git show HEAD~1:${file} | head -n 10 | egrep -o -e "Copyright ([[:digit:]]{4})")
  new_copyright=$(cat ${file} | head -n 10 | egrep -o -e "Copyright ([[:digit:]]{4})")
  if [ ! -z "${old_copyright}" ] && [ ! -z "${new_copyright}" ] && [ "${old_copyright}" != "${new_copyright}" ]
  then
    echo "Restoring copyright in ${file} to '${old_copyright}'"
    sed -i "s/${new_copyright}/${old_copyright}/1" ${file}
  fi
done
