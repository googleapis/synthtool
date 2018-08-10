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

from synthtool import _tracked_paths
from synthtool import cache
from synthtool import shell


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
