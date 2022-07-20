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

# Runs template and etc in current working directory
function processModule() {
  # templates
  echo "Generating templates..."
  /owlbot/bin/write_templates.sh
  echo "...done"

  # write or restore pom.xml files
  echo "Generating missing pom.xml..."
  /owlbot/bin/write_missing_pom_files.sh
  echo "...done"

  # write or restore clirr-ignored-differences.xml
  echo "Generating clirr-ignored-differences.xml..."
  /owlbot/bin/write_clirr_ignore.sh
  echo "...done"

  # fix license headers
  echo "Fixing missing license headers..."
  /owlbot/bin/fix_license_headers.sh
  echo "...done"

  # TODO: re-enable this once we resolve thrashing
  # restore license headers years
  # echo "Restoring copyright years..."
  # /owlbot/bin/restore_license_headers.sh
  # echo "...done"

  # ensure formatting on all .java files in the repository
  echo "Reformatting source..."
  /owlbot/bin/format_source.sh
  echo "...done"
}

if [ "$(find . -type d -name 'java-*' |wc -l)" -gt 10 ];then
  # Monorepo (googleapis/google-cloud-java)
  echo "Processing monorepo"
  if [ -d owl-bot-staging ]; then
    # The content of owl-bot-staging is controlled by Owlbot.yaml files in
    # each module in the monorepo
    echo "Extracting contents from owl-bot-staging"
    for module in $(ls owl-bot-staging); do
      if [ ! -d "$module" ]; then
        continue
      fi
      # This relocation allows us continue to use owlbot.py without modification
      # after monorepo migration.
      mv "owl-bot-staging/$module" "$module/owl-bot-staging"
      pushd "$module"
      processModule
      popd
    done
    rm -r owl-bot-staging
  else
    echo "In monorepo but no owl-bot-staging." \
        "Formatting changes in the last commit"
    # Find the files that were touched by the last commit.
    last_commit=$(git log -1 --format=%H)
    # [A]dded, [C]reated, [M]odified, and [R]enamed
    changed_files=$(git show --name-only --no-renames --diff-filter=ACMR \
        "${last_commit}")
    changed_modules=$(echo "$changed_files" |grep -E '.java$' |cut -d '/' -f 1 \
        |sort -u)
    for module in ${changed_modules}; do
      if [ ! -f "$module/.OwlBot.yaml" ]; then
        # Changes irrelevant to Owlbot-generated module (such as .github) do not
        # need formatting
        continue
      fi
      pushd "$module"
      processModule
      popd
    done
  fi
else
  # Individual repository
  echo "Processing a single repo"
  processModule
fi