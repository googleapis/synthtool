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
import os
import re


from autosynth import github


def list_repositories():
    """List all the available discovery versions grouped by api"""
    gh = github.GitHub(os.environ["GITHUB_TOKEN"])

    repo = "googleapis/elixir-google-api"
    api_config = gh.get_contents(repository=repo, path="config/apis.json")

    api_names = set()
    for api in json.loads(api_config):
        api_names.add(api["name"])

    return [
        {
            "name": api,
            "repository": "googleapis/elixir-google-api",
            "branch-suffix": api.lower(),
            "pr-title": f"Regenerate {api} client",
            "args": [api],
            "metadata-path": f"clients/{_underscore(api)}",
        }
        for api in sorted(api_names)
    ]


def _underscore(name: str) -> str:
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-z])([A-Z])", r"\1_\2", name)
    return name.lower()


if __name__ == "__main__":
    import yaml

    print(yaml.dump(list_repositories()))
