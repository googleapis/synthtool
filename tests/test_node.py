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
from synthtool.languages import node

FIXTURES = Path(__file__).parent / "fixtures" / "node_templates"


def test_quickstart_metadata_with_snippet():
    cwd = os.getcwd()
    os.chdir(FIXTURES / "standard")

    metadata = node._template_metadata()

    # should have loaded the special quickstart sample (ignoring header).
    assert "ID of the Cloud Bigtable instance" in metadata["quickstart"]
    assert "limitations under the License" not in metadata["quickstart"]

    # should have a link to the quickstart in the samples
    sample_names = list(map(lambda sample: sample["file"], metadata["samples"]))
    assert "samples/quickstart.js" in sample_names

    os.chdir(cwd)


def test_quickstart_metadata_without_snippet():
    cwd = os.getcwd()
    os.chdir(FIXTURES / "no_quickstart_snippet")

    metadata = node._template_metadata()

    # should not have populated the quickstart for the README
    assert not metadata["quickstart"]

    # should not have a link to the quickstart in the samples
    sample_names = list(map(lambda sample: sample["file"], metadata["samples"]))
    assert "samples/quickstart.js" not in sample_names

    os.chdir(cwd)
