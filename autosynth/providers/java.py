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

from autosynth.providers.list_split_repositories import list_split_repositories


def list_repositories():
    repos = list_split_repositories("java", ("Java",))
    # Ignore apiary services repo (has separate provider)
    return [repo for repo in repos if repo["name"] != "google-api-java-client-services"]


if __name__ == "__main__":
    import yaml

    print(yaml.dump(list_repositories()))
