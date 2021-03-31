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
