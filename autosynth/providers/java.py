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

from autosynth import github


def list_repositories():
    gh = github.GitHub(os.environ["GITHUB_TOKEN"])
    all_repos = gh.list_repos("googleapis")
    java_repos = [repo for repo in all_repos if "java" in repo.split("-")]
    synth_repos = []
    java_repos.sort()
    for repo in java_repos:
        # Ignore apiary services repo (has separate provider)
        if repo == "google-api-java-client-services":
            continue
        # Only repos with a synth.py in the top-level directory.
        if not gh.list_files(f"googleapis/{repo}", "synth.py"):
            continue
        synth_repos.append({"name": repo, "repository": f"googleapis/{repo}"})
    return synth_repos


if __name__ == "__main__":
    import yaml

    print(yaml.dump(list_repositories()))
