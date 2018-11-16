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
import re
import shutil
import subprocess
from typing import Dict, Tuple

from synthtool import _tracked_paths
from synthtool import cache
from synthtool import metadata
from synthtool import shell

REPO_REGEX = (
    r"(((https:\/\/)|(git@))github.com(:|\/))?(?P<owner>[^\/]+)\/(?P<name>[^\/]+)"
)

USE_SSH = os.environ.get("AUTOSYNTH_USE_SSH", False)


def make_repo_clone_url(repo: str) -> str:
    """Returns a fully-qualified repo URL on GitHub from a string containing
    "owner/repo".

    This returns an https URL by default, but will return an ssh URL if
    AUTOSYNTH_USE_SSH is set.
    """
    if USE_SSH:
        return f"git@github.com:{repo}.git"
    else:
        return f"https://github.com/{repo}.git"


def clone(
    url: str,
    dest: pathlib.Path = None,
    committish: str = "master",
    force: bool = False,
    depth: int = None,
) -> pathlib.Path:
    if dest is None:
        dest = cache.get_cache_dir()

    dest = dest / pathlib.Path(url).stem

    if force and dest.exists():
        shutil.rmtree(dest)

    if not dest.exists():
        cmd = ["git", "clone", url, dest]
        if depth is not None:
            cmd.extend(["--depth", str(depth)])
        shell.run(cmd)
    else:
        shell.run(["git", "pull"], cwd=str(dest))

    shell.run(["git", "reset", "--hard", committish], cwd=str(dest))

    # track all git repositories
    _tracked_paths.add(dest)

    # add repo to metadata
    sha, message = get_latest_commit(dest)
    commit_metadata = extract_commit_message_metadata(message)

    metadata.add_git_source(
        name=dest.name,
        remote=url,
        sha=sha,
        internal_ref=commit_metadata.get("PiperOrigin-RevId"),
    )

    return dest


def parse_repo_url(url: str) -> Dict[str, str]:
    """
    Parses a GitHub url and returns a dict with:
        owner - Owner of the repository
        name  - Name of the repository

    The following are matchable:
        googleapis/nodejs-vision(.git)?
        git@github.com:GoogleCloudPlatform/google-cloud-python.git
        https://github.com/GoogleCloudPlatform/google-cloud-python.git
    """
    match = re.search(REPO_REGEX, url)

    if not match:
        raise RuntimeError("repository url is not a properly formatted git string.")

    owner = match.group("owner")
    name = match.group("name")

    if name.endswith(".git"):
        name = name[:-4]

    return {"owner": owner, "name": name}


def get_latest_commit(repo: pathlib.Path = None) -> Tuple[str, str]:
    """Return the sha and commit message of the latest commit."""
    output = subprocess.check_output(
        ["git", "log", "-1", "--pretty=%H%n%B"], cwd=repo
    ).decode("utf-8")
    commit, message = output.split("\n", 1)
    return commit, message


def extract_commit_message_metadata(message: str) -> Dict[str, str]:
    """Extract extended metadata stored in the Git commit message.

    For example, a commit that looks like this::

        Do the thing!

        Piper-Changelog: 1234567

    Will return::

        {"Piper-Changelog": "1234567"}

    """
    metadata = {}
    for line in message.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        metadata[key] = value.strip()

    return metadata
