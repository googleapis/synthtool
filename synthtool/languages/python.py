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

import json
import re

_REQUIRED_FIELDS = ["version"]


def read_metadata():
    """
    read version from setup.py of a Python library.

    Returns:
        data - package.json file as a dict.
    """
    data = {}
    with open("./setup.py") as f:
        contents = f.read()
        match = re.search(r"version\s*=\s*['\"](.+?)['\"]", contents)
        if match:
            data['version'] = match.group(1)

        if not all(key in data for key in _REQUIRED_FIELDS):
            raise RuntimeError(
                f"setup.py is missing required fields {_REQUIRED_FIELDS}"
        )

    return data