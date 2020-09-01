# Copyright 2019 Google LLC
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

    # Presently this only enumerates folders from the google-cloud-dotnet
    # monorepo, under the autosynth directory.
    repo = "googleapis/google-cloud-dotnet"

    clients = gh.list_files(repo, "apis")
    subdirs = [item["path"] for item in clients if item["type"] == "dir"]

    # No hidden dirs
    subdirs = [subdir for subdir in subdirs if not subdir.startswith(".")]

    # Only subdirs that have synth.py files.
    subdirs = [
        subdir for subdir in subdirs if gh.check_for_file(repo, f"{subdir}/synth.py")
    ]

    return [_config_for_subdir(repo, subdir) for subdir in subdirs]


def _config_for_subdir(repo: str, subdir: str):
    api = subdir.split("/")[1]

    return {
        "name": api,
        "repository": repo,
        "synth-path": subdir,
        "branch-suffix": api,
        "pr-title": f"Regenerate {api}",
    }


if __name__ == "__main__":
    import yaml

    print(yaml.dump(list_repositories()))
