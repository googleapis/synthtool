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


if [ -f synth.py ]
then
  # convert synth.py to owlbot.py + .github/.OwlBot.yaml
  python3 /owlbot/src/convert-synth.py
fi

if [ -f owlbot.py ]
then
  # if owlbot.py exists, ensure the formatting is correct
  python3 -m black owlbot.py
fi
