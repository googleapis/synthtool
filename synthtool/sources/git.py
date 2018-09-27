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

import pathlib
import shutil
import re
from typing import Dict

from synthtool import _tracked_paths
from synthtool import cache
from synthtool import shell

REPO_REGEX = (
    r"(((https:\/\/)|(git@))github.com(:|\/))?(?P<owner>[^\/]+)\/(?P<name>[^\/]+)"
)


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
