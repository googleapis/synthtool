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
from typing import Optional, Union
import os

from synthtool.log import logger
from synthtool.sources import git

GOOGLEAPIS_GEN_URL: str = git.make_repo_clone_url("googleapis/googleapis-gen")
LOCAL_GOOGLEAPIS_GEN: Optional[str] = os.environ.get("SYNTHTOOL_GOOGLEAPIS_GEN")


class Pregenerated:
    """A synthtool component that copies pregenerated bazel code."""

    def __init__(self):
        if LOCAL_GOOGLEAPIS_GEN:
            self._googleapis_gen = Path(LOCAL_GOOGLEAPIS_GEN).expanduser()
            logger.debug(f"Using local googleapis-gen at {self._googleapis_gen}")
        else:
            logger.debug("Cloning googleapis-gen.")
            self._googleapis_gen = git.clone(GOOGLEAPIS_GEN_URL)

    def generate(self, path: str) -> Path:
        return self._googleapis_gen / path
