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
from pathlib import Path

from synthtool import gcp


def test_python_library():
    os.chdir(Path(__file__).parent / "fixtures/python_library")
    template_dir = Path(__file__).parent.parent / "synthtool/gcp/templates"
    common = gcp.CommonTemplates(template_path=template_dir)
    templated_files = common.py_library()

    assert os.path.exists(
        templated_files / ".kokoro/docs/docs-presubmit.cfg")
    assert os.path.exists(
        templated_files / ".kokoro/docker/docs/fetch_gpg_keys.sh")
