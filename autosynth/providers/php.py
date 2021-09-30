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
    # Presently this only enumerates folders from the google-cloud-php
    # monorepo.
    repo = "googleapis/google-cloud-php"

    default_branch = gh.get_default_branch(repo)
    tree = gh.get_tree(repo, default_branch)
    subdirs = [item["path"] for item in tree["tree"] if item["type"] == "tree"]
    # No hidden dirs
    subdirs = [subdir for subdir in subdirs if not subdir.startswith(".")]
    # Only subdirs that have synth.py files.
    subdirs = [
        subdir for subdir in subdirs if gh.check_for_file(repo, f"{subdir}/synth.py")
    ]

    return [
        {
            "name": subdir.lower(),
            "repository": repo,
            "synth-path": subdir,
            "branch-suffix": subdir.lower(),
        }
        for subdir in subdirs
    ]


if __name__ == "__main__":
    import yaml

    print(yaml.dump(list_repositories()))
