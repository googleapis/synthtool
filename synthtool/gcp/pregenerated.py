# Copyright 2021 Google LLC
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

from pathlib import Path
import os

from synthtool.log import logger
from synthtool.sources import git


class Pregenerated:
    """A synthtool component that copies pregenerated bazel code."""

    def __init__(self):
        local_clone = os.environ.get("SYNTHTOOL_GOOGLEAPIS_GEN")
        if local_clone:
            self._googleapis_gen = Path(local_clone).expanduser()
            logger.debug(f"Using local googleapis-gen at {self._googleapis_gen}")
        else:
            logger.debug("Cloning googleapis-gen.")
            self._googleapis_gen = git.clone(
                git.make_repo_clone_url("googleapis/googleapis-gen")
            )

    def generate(self, path: str) -> Path:
        return self._googleapis_gen / path
