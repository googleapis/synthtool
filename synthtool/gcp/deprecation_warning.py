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

import os
import yaml
from pathlib import Path
from typing import Dict, List

# these are the default locations to look up
_DEFAULT_WARNING_FILES = [".readme-deprecation-warning.yml", ".readme-deprecation-warning.yaml"]


def load_warning(files: List[str] = _DEFAULT_WARNING_FILES) -> Dict:
  """
  hand-crafted artisanal markdown can be provided in a .readme-deprecation-warning.yml.
  The following fields are currently supported:

  warning: custom warning with deprecation notice and redirect link to alternate library
  """
  cwd_path = Path(os.getcwd())
  warning_file = None
  for file in files:
    if os.path.exists(cwd_path / file):
      warning_file = cwd_path / file
      break
  if not warning_file:
    return {}
  with open(warning_file) as f:
    return yaml.load(f, Loader=yaml.SafeLoader)
