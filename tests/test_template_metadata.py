# Copyright 2019 Google LLC
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

from synthtool.gcp.templates.metadata import Metadata

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_samples():
    cwd = os.getcwd()
    os.chdir(FIXTURES)

    metadata = Metadata()

    # should have loaded samples.
    assert metadata["samples"][3]["title"] == "Requester Pays"
    assert metadata["samples"][3]["file"] == "requesterPays.js"
    assert len(metadata["samples"]) == 4
    # should have loaded the special quickstart sample (ignoring header).
    assert "ID of the Cloud Bigtable instance" in metadata["quickstart"]
    assert "limitations under the License" not in metadata["quickstart"]
    # should have included additional meta-information provided.
    assert metadata["samples"][0]["title"] == "Metadata Example 1"
    assert metadata["samples"][0]["usage"] == "node hello-world.js"
    assert metadata["samples"][1]["title"] == "Metadata Example 2"
    assert metadata["samples"][1]["usage"] == "node goodnight-moon.js"

    os.chdir(cwd)


def test_readme_partials():
    cwd = os.getcwd()
    os.chdir(FIXTURES)

    metadata = Metadata()

    # should have populated introduction from partial.
    assert (
        "objects to users via direct download" in metadata["partials"]["introduction"]
    )

    os.chdir(cwd)
