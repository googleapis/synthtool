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

def read_metadata():
    """
    read package name and repository in package.json from a Node library.

    Returns:
        package_name: Name of the package (with scope)
        repo_name: Name of the repository
    """
    with open('./package.json') as f:
        data = json.load(f)

        package_name = data['name']
        repo_name = data['repository']

        if package_name is None:
            raise RuntimeError("package.json is missing name field")
        if repo_name is None:
            raise RuntimeError("package.json is missing repository field")

        return {'package_name': package_name, 'repo_name': repo_name}
