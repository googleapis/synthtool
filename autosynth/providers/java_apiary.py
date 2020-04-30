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

from autosynth.providers import apiary


def list_repositories():
    api_names = apiary.list_apis().keys()

    repositories = [
        {
            "name": api,
            "repository": "googleapis/google-api-java-client-services",
            "branch-suffix": api,
            "pr-title": f"Regenerate {api} client",
            "args": [api],
            "metadata-path": f"clients/google-api-services-{api}",
        }
        for api in api_names
    ]
    repositories.append(
        {
            "name": "README",
            "repository": "googleapis/google-api-java-client-services",
            "branch-suffix": "readme",
            "pr-title": f"Regenerate client list in README",
            "args": ["README"],
        }
    )
    return repositories


if __name__ == "__main__":
    import yaml

    print(yaml.dump(list_repositories()))
