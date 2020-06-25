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
import pathlib
from typing import Dict, List

import yaml

from autosynth import github


def list_split_repositories(lang: str) -> List[Dict]:
    """Finds repos in github named like *-lang-*, and combines with lang-addendum.yaml."""
    # Load the repo list from the addendum.
    text = open(pathlib.Path(__file__).parent / f"{lang}-addendum.yaml", "rt").read()
    addendum = list(yaml.safe_load(text) or [])
    # Find repos on github.
    repos = _list_github_repositories(lang) + addendum
    repos.sort(key=lambda x: x["name"])
    return repos


def _list_github_repositories(lang: str) -> List[Dict]:
    """Find repos on github with a matching named and synth.py file."""
    gh = github.GitHub(os.environ["GITHUB_TOKEN"])
    all_repos = gh.list_repos("googleapis")
    lang_repos = [repo for repo in all_repos if lang in repo.split("-")]
    synth_repos = []
    for repo in lang_repos:
        # Only repos with a synth.py in the top-level directory.
        if not gh.list_files(f"googleapis/{repo}", "synth.py"):
            continue
        synth_repos.append({"name": repo, "repository": f"googleapis/{repo}"})
    return synth_repos
