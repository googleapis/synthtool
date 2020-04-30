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

from autosynth import github


def list_repositories():
    gh = github.GitHub(os.environ["GITHUB_TOKEN"])

    return _google_cloud_java_repos(gh) + _other_repos(gh)


def _google_cloud_java_repos(gh):
    # Presently this only enumerates folders from the google-cloud-java
    # monorepo.
    repo = "googleapis/google-cloud-java"

    clients = gh.list_files(repo, "google-cloud-clients")
    subdirs = [item["path"] for item in clients if item["type"] == "dir"]

    # No hidden dirs
    subdirs = [subdir for subdir in subdirs if not subdir.startswith(".")]

    # Only subdirs that have synth.py files.
    subdirs = [
        subdir for subdir in subdirs if gh.check_for_file(repo, f"{subdir}/synth.py")
    ]

    return [_config_for_subdir(repo, subdir) for subdir in subdirs]


def _other_repos(gh):
    repos = _get_repo_list_from_sloth(gh)
    repos = [repo for repo in repos if _is_java_synth_repo(gh, repo)]

    return [
        {"name": repo["repo"].split("/")[-1], "repository": repo["repo"]}
        for repo in repos
    ]


def _config_for_subdir(repo: str, subdir: str):
    api = subdir.split("/")[1].replace("google-cloud-", "")

    return {
        "name": api,
        "repository": repo,
        "synth-path": subdir,
        "branch-suffix": api,
        "pr-title": f"Regenerate {api} client",
    }


def _get_repo_list_from_sloth(gh):
    contents = gh.get_contents("googleapis/sloth", "repos.json")
    repos = json.loads(contents)["repos"]
    return repos


def _is_java_synth_repo(gh, repo):
    # Only java repos.
    if repo["language"] != "java":
        return False
    # No private repos.
    if "private" in repo["repo"]:
        return False
    # Only repos with a synth.py in the top-level directory.
    if not gh.check_for_file(repo["repo"], "synth.py"):
        return False
    # Ignore apiary services repo (has separate provider)
    if repo["repo"] == "googleapis/google-api-java-client-services":
        return False

    return True


if __name__ == "__main__":
    import yaml

    print(yaml.dump(list_repositories()))
