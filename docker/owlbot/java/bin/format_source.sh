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

# Find all the java files relative to the current directory and format them
# using google-java-format
list="$(find . -name '*.java' )"
tmpfile=$(mktemp)

for file in $list;
do
  if [[ $file =~ .*/samples/snippets/src/main/java/com/example/firestore/Quickstart.java ]];
  then
    echo "File skipped formatting: $file"
  elif [[ $file =~ .*/samples/snippets/src/.*/java/com/example/spanner/.*.java ]];
  then
    echo "File skipped formatting: $file"
  else
   echo $file >> $tmpfile
  fi
done

cat $tmpfile | xargs java -jar /owlbot/google-java-format.jar --replace

rm $tmpfile