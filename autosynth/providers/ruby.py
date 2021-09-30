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
import requests

from autosynth import github


def list_repositories():
    gh = github.GitHub(os.environ["GITHUB_TOKEN"])

    # Presently this only enumerates folders from the google-cloud-ruby
    # monorepo.
    repo = "googleapis/google-cloud-ruby"

    default_branch = gh.get_default_branch(repo)
    tree = gh.get_tree(repo, default_branch)
    subdirs = [item["path"] for item in tree["tree"] if item["type"] == "tree"]
    # No hidden dirs
    subdirs = [subdir for subdir in subdirs if not subdir.startswith(".")]
    # Only subdirs that have synth.py files.
    subdirs = [subdir for subdir in subdirs if _check_bazel_synth(gh, repo, subdir)]

    return [
        {
            "name": subdir.replace("google-cloud-", ""),
            "repository": repo,
            "synth-path": subdir,
            "branch-suffix": subdir.replace("google-cloud-", ""),
        }
        for subdir in subdirs
    ]


def _check_bazel_synth(gh, repo: str, subdir: str) -> bool:
    try:
        contents = gh.get_contents(repo, f"{subdir}/synth.py").decode("utf-8")
        return "gcp.GAPICBazel" in contents
    except requests.exceptions.HTTPError:
        return False


if __name__ == "__main__":
    import yaml

    print(yaml.dump(list_repositories()))
