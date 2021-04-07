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
from pathlib import Path

from synthtool.gcp import deprecation_warning

FIXTURES = Path(__file__).parent / "fixtures" / "node_templates" / "standard"


def test_readme_deprecation_warning():
  cwd = os.getcwd()
  os.chdir(FIXTURES)

  data = deprecation_warning.load_warning()
  # should have populated introduction from deprecation warning.
  assert "## This is a test warning" in data["warning"]

  os.chdir(cwd)


def test_readme_deprecation_warning_not_found():
  data = deprecation_warning.load_warning(["non-existent.yaml"])
  assert len(data) == 0
