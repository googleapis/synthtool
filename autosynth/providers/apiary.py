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

import os
import re

from autosynth import github
from typing import Dict, List

VERSION_REGEX = re.compile("(.*)\\.(v.*).json")


def list_apis() -> Dict[str, List[str]]:
    """List all the available discovery versions grouped by api"""
    gh = github.GitHub(os.environ["GITHUB_TOKEN"])

    # List discovery documents from discovery-artifact-manager
    repo = "googleapis/discovery-artifact-manager"

    # Find the unique API names
    apis = {}
    files = gh.list_files(repo, "discoveries")
    discoveries = [file["name"] for file in files if file["name"].endswith(".json")]
    for discovery in discoveries:
        m = VERSION_REGEX.match(discovery)
        if m:
            api = m.group(1)
            version = m.group(2)

            if api not in apis:
                apis[api] = []

            apis[api].append(version)

    return apis


if __name__ == "__main__":
    import yaml

    print(yaml.dump(list_apis()))
