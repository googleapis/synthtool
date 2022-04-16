# Copyright 2022 Google LLC
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

from synthtool.languages import common
from pathlib import Path
import json
import shutil
import numpy as np

FIXTURES_SAMPLES = Path(__file__).parent / "fixtures" / "samples" / "generated"


def test_get_sample_metadata_files():
    metadataFiles = [
        str(
            Path.resolve(
                FIXTURES_SAMPLES / "v1" / "snippet_metadata.google.cloud.asset.v1.json"
            )
        ),
        str(
            Path.resolve(
                FIXTURES_SAMPLES / "v2" / "snippet_metadata.google.cloud.asset.v2.json"
            )
        ),
    ]
    assert np.array_equal(
        common.get_sample_metadata_files(Path.resolve(FIXTURES_SAMPLES)), metadataFiles
    )


def test_update_library_version():
    shutil.copytree(FIXTURES_SAMPLES, Path.resolve(FIXTURES_SAMPLES / "temp"))
    with open(
        Path.resolve(
            FIXTURES_SAMPLES
            / "temp"
            / "v1"
            / "snippet_metadata.google.cloud.asset.v1.json"
        ),
        "r+",
    ) as n:
        common.update_library_version("1234", FIXTURES_SAMPLES / "temp")
        new_data = json.load(n)
        assert new_data["clientLibrary"]["version"] == "1234"

    with open(
        Path.resolve(
            FIXTURES_SAMPLES
            / "temp"
            / "v2"
            / "snippet_metadata.google.cloud.asset.v2.json"
        ),
        "r+",
    ) as n:
        common.update_library_version("1234", FIXTURES_SAMPLES / "temp")
        new_data = json.load(n)
        assert new_data["clientLibrary"]["version"] == "1234"

    shutil.rmtree(Path.resolve(FIXTURES_SAMPLES / "temp"))
