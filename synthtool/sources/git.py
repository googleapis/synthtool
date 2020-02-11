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

import functools
import os
import pathlib
import re
import shutil
import subprocess
from typing import Dict, Optional, Tuple

import google.protobuf
from synthtool import _tracked_paths, cache, metadata, shell
from synthtool.protos.preconfig_pb2 import Preconfig

REPO_REGEX = (
    r"(((https:\/\/)|(git@))github.com(:|\/))?(?P<owner>[^\/]+)\/(?P<name>[^\/]+)"
)

USE_SSH = os.environ.get("AUTOSYNTH_USE_SSH", False)

PRECONFIG_ENVIRONMENT_VARIABLE = "SYNTHTOOL_PRECONFIG_FILE"

PRECONFIG_HELP = """
A json file containing a description of prefetch sources that this synth.py may
us.  See preconfig.proto for detail about the format.
"""


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
    url: str, dest: pathlib.Path = None, committish: str = None, force: bool = False,
) -> pathlib.Path:
    preclone = get_preclone(url)

    if preclone:
        dest = pathlib.Path(preclone)
    else:
        if dest is None:
            dest = cache.get_cache_dir()

        dest = dest / pathlib.Path(url).stem

        if force and dest.exists():
            shutil.rmtree(dest)

        if not dest.exists():
            cmd = ["git", "clone", "--single-branch", url, dest]
            shell.run(cmd)
        else:
            shell.run(["git", "pull"], cwd=str(dest))
        committish = committish or "master"

    if committish:
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
        local_path=str(dest),
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


@functools.lru_cache(maxsize=None)
def _load_preconfig():
    """Loads the preconfig file specified in an environment variable.

    Returns:
      An instance of Preconfig
    """
    preconfig_file_path = os.environ.get(PRECONFIG_ENVIRONMENT_VARIABLE)
    if not preconfig_file_path:
        return Preconfig()
    with open(preconfig_file_path, "rt") as json_file:
        return google.protobuf.json_format.Parse(json_file.read(), Preconfig())


def get_preclone(url: str) -> Optional[str]:
    """Finds a pre-cloned git repo in the preclone map."""
    preconfig = _load_preconfig()
    return preconfig.precloned_repos.get(url)
