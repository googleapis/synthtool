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
from pathlib import Path
import pytest

from synthtool.languages import python_mono_repo
from . import util


TEST_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "python_mono_repo"


def test_apply_workaround():
    with util.copied_fixtures_dir(TEST_FIXTURE_DIR):
        docs_index_rst = Path(
            "packages/google-cloud-workflows/docs/index.rst"
        ).read_text()
        assert (
            docs_index_rst
            == "First replacement\nFirst replacement\nSecond replacement\n"
        )
        python_mono_repo.apply_client_specific_post_processing(
            "packages/google-cloud-workflows/scripts/client-post-processing",
            "google-cloud-workflows",
        )
        docs_index_rst = Path(
            "packages/google-cloud-workflows/docs/index.rst"
        ).read_text()
        assert (
            docs_index_rst
            == "Completed replacement 1.\nCompleted replacement 1.\nCompleted replacement 2.\n"
        )

        # Confirm that `AssertionError`` is raised if you run the post processing more than once
        # because the replacement should only occur once.
        with pytest.raises(AssertionError):
            python_mono_repo.apply_client_specific_post_processing(
                "packages/google-cloud-workflows/scripts/client-post-processing",
                "google-cloud-workflows",
            )
