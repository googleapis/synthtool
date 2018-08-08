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
from pathlib import Path

from synthtool import _tracked_paths
from synthtool import log
from synthtool import shell
from synthtool.sources import git

class RepositoryGenerator:
    def __init__(self, repository):

        self._clone_repository(repository)

    def repository_library(self, commands, env=None) -> Path:
        """
        Generates the client library files using a temporary git repository
        returns a `Path` object
        """

        log.debug(f"Running generator.")

        for command in commands:
            log.debug(f"Running command: `{command}`.")
            shell.run(command.split(), cwd=self.repository, env=env)

        return self.repository

    def _clone_repository(self, repository):

        log.debug(f"Cloning repository {repository}.")
        self.repository = git.clone(repository, depth=1)
        _tracked_paths.add(self.repository)
