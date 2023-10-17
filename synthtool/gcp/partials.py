# Copyright 2020 Google LLC
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
import yaml
from pathlib import Path
from typing import Dict, List

# these are the default locations to look up
_DEFAULT_PARTIAL_FILES = [
    ".readme-partials.yml",
    ".readme-partials.yaml",
    ".integration-partials.yaml",
]


def load_partials(files: List[str] = []) -> Dict:
    """
    hand-crafted artisanal markdown can be provided in a .readme-partials.yml.
    The following fields are currently supported:

    body: custom body to include in the usage section of the document.
    samples_body: an optional body to place below the table of contents
        in samples/README.md.
    introduction: a more thorough introduction than metadata["description"].
    title: provide markdown to use as a custom title.
    deprecation_warning: a warning to indicate that the library has been
        deprecated and a pointer to an alternate option
    """
    result: Dict[str, Dict] = {}
    cwd_path = Path(os.getcwd())
    for file in files + _DEFAULT_PARTIAL_FILES:
        partials_file = cwd_path / file
        if os.path.exists(partials_file):
            with open(partials_file) as f:
                result.update(yaml.load(f, Loader=yaml.SafeLoader))
    return result
