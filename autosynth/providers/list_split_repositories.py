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
from typing import Dict, List, Sequence

from autosynth import github

"""Chunks that identify a repo from its name as belonging to a language.

In other words, we can look at the repo name python-spanner and know that it's
for a python library because it contains the word 'python'.
"""
_SILVER_NAME_CHUNKS = (
    "nodejs",
    "python",
    "ruby",
    "dotnet",
    "php",
    "java",
    "go",
    "elixir",
)

"""Language names as reported by github."""
_SILVER_LANGUAGE_NAMES = (
    "JavaScript",
    "TypeScript",
    "Python",
    "Java",
    "PHP",
    "Ruby",
    "Go",
    "C#",
    "Elixir",
)


def list_split_repositories(
    repo_name_chunk: str, majority_languages: Sequence[str] = ()
) -> List[Dict]:
    """List github repos for a programming language.

    Args:
        repo_name_chunk (str): return repos that have this chunk in the repo name.
            Example: "nodejs"
        majority_languages (Sequence[str], optional): return repos that have a majority
            of their code written in one of these programming languages.
            Example: ("JavaScript", "TypeScript")

    Returns:
        List[Dict]: [description]
    """

    gh = github.GitHub(os.environ["GITHUB_TOKEN"])
    all_repos = set(
        [repo["name"] for repo in gh.list_repos("googleapis") if not repo["archived"]]
    )
    # Find repos with the language as part of the repo name.
    lang_repos = set([repo for repo in all_repos if repo_name_chunk in repo.split("-")])
    if majority_languages:
        # Ignore all repos whose name tags them for a language.
        silver_name_chunks = set(_SILVER_NAME_CHUNKS)
        all_lang_repos = set(
            [
                repo
                for repo in all_repos
                if silver_name_chunks.intersection(set(repo.split("-")))
            ]
        )
        # Find repos with the majority of their code written in the language.
        silver_language_names = set(_SILVER_LANGUAGE_NAMES)
        for repo in all_repos - all_lang_repos:
            languages = gh.get_languages(f"googleapis/{repo}")
            ranks = [
                (count, lang)
                for (lang, count) in languages.items()
                # Ignore languages we don't care about, like Shell.
                if lang in silver_language_names
            ]
            if ranks and max(ranks)[1] in majority_languages:
                lang_repos.add(repo)

    synth_repos = []
    for repo in sorted(lang_repos):
        # Only repos with a synth.py in the top-level directory.
        if not gh.list_files(f"googleapis/{repo}", "synth.py"):
            continue
        synth_repos.append({"name": repo, "repository": f"googleapis/{repo}"})
    return synth_repos
