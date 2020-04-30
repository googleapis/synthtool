#!/usr/bin/env python3.6
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os

from abc import ABC, abstractmethod
from autosynth import git, github
from autosynth.log import logger
import subprocess
import uuid
import tempfile


class AbstractChangePusher(ABC):
    """Abstractly, the thing that pushes changes to github."""

    @abstractmethod
    def push_changes(
        self, commit_count: int, branch: str, pr_title: str, synth_log: str = ""
    ) -> None:
        """Creates a pull request from commits in current working directory."""
        pass

    @abstractmethod
    def check_if_pr_already_exists(self, branch) -> bool:
        pass


class ChangePusher(AbstractChangePusher):
    """Actually pushes changes to github."""

    def __init__(self, repository: str, gh: github.GitHub, synth_path: str):
        self._repository = repository
        self._gh = gh
        self._synth_path = synth_path

    def push_changes(
        self, commit_count: int, branch: str, pr_title: str, synth_log: str = ""
    ) -> None:
        git.push_changes(branch)

        pr = self._gh.create_pull_request(
            self._repository,
            branch=branch,
            title=pr_title,
            body=build_pr_body(synth_log),
        )

        # args.synth_path (and api: * labels) only exist in monorepos
        if self._synth_path:
            api_label = self._gh.get_api_label(self._repository, self._synth_path)

            if api_label:
                self._gh.update_pull_labels(json.loads(pr), add=[api_label])

    def check_if_pr_already_exists(self, branch) -> bool:
        repo = self._repository
        owner = repo.split("/")[0]
        prs = self._gh.list_pull_requests(repo, state="open", head=f"{owner}:{branch}")

        if prs:
            pr = prs[0]
            logger.info(f'PR already exists: {pr["html_url"]}')
        return bool(prs)


class SquashingChangePusher(AbstractChangePusher):
    """Wraps another change pusher to squash all commits into a single commit

    before pushing the pull request to github."""

    def __init__(self, inner_change_pusher: AbstractChangePusher):
        self.inner_change_pusher = inner_change_pusher

    def push_changes(
        self, commit_count: int, branch: str, pr_title: str, synth_log: str = ""
    ) -> None:
        if commit_count < 2:
            # Only one change, no need to squash.
            self.inner_change_pusher.push_changes(
                commit_count, branch, pr_title, synth_log
            )
            return

        subprocess.check_call(["git", "checkout", branch])  # Probably redundant.
        with tempfile.NamedTemporaryFile() as message_file:
            # Collect the commit messages into a temporary file.
            subprocess.run(
                ["git", "log", f"-{commit_count}", "--format=* %s%n%b"],
                stdout=message_file,
                check=True,
            )
            message_file.file.close()  # type: ignore
            # Do a git dance to construct a branch with the commits squashed.
            temp_branch = str(uuid.uuid4())
            subprocess.check_call(["git", "branch", "-m", temp_branch])
            subprocess.check_call(["git", "checkout", "master"])
            subprocess.check_call(["git", "checkout", "-b", branch])
            subprocess.check_call(["git", "merge", "--squash", temp_branch])
            subprocess.check_call(["git", "commit", "-F", message_file.name])
        self.inner_change_pusher.push_changes(1, branch, pr_title, synth_log)

    def check_if_pr_already_exists(self, branch) -> bool:
        return self.inner_change_pusher.check_if_pr_already_exists(branch)


def build_pr_body(synth_log: str):
    """Composes the pull request body with the synth_log.

    If synth_log is empty, then creates link to kokoro build log.
    """
    build_log_text = ""
    kokoro_build_id = os.environ.get("KOKORO_BUILD_ID")
    if synth_log:
        build_log_text = f"""
<details><summary>Log from Synthtool</summary>

```
{synth_log}
```
</details>"""
    elif kokoro_build_id:
        build_log_text = f"""Synth log will be available here:
https://source.cloud.google.com/results/invocations/{kokoro_build_id}/targets"""

    return f"""\
This PR was generated using Autosynth. :rainbow:

{build_log_text}
""".strip()
