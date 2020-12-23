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

from autosynth.providers import apiary
import re


def list_repositories():
    repositories = [
        {
            "name": f"{name}-{version}",
            "repository": "googleapis/google-api-ruby-client",
            "branch-suffix": f"{name}-{version}",
            "args": [name, version],
            "metadata-path": f"google-api-client/generated/google/apis/{_client_dir(name, version)}",
            "pr-title": f"feat: Automated regeneration of {name} {version} client",
        }
        for name, versions in apiary.list_apis().items() for version in versions
    ]

    repositories.append(
        {
            "name": "clean",
            "repository": "googleapis/google-api-ruby-client",
            "branch-suffix": "clean",
            "args": ["clean"],
            "pr-title": "feat: Automated removal of obsolete clients",
        }
    )

    return repositories


def _client_dir(name: str, version: str) -> str:
    """Determines the code directory name for a generated API client.

    This effectively converts the API name and version to underscore case,
    and matches the logic in the Ruby Apiary generator.

    Arguments:
        name {str} -- The name of the API being generated
        version {str} -- The version of the API being generated

    Returns:
        str -- Directory name
    """
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-z])([A-Z])", r"\1_\2", name)
    name = name.lower()
    version = version.replace(".", "_").lower()
    return f"{name}_{version}"


if __name__ == "__main__":
    import yaml

    print(yaml.dump(list_repositories()))
