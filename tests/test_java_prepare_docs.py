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

from synthtool.gcp.templates.java_library.prepare_docs import prepare_toc
import unittest
import shutil
import filecmp
import yaml
import pytest

mock_original_toc = "tests/testdata/mock-java-original-toc.yml"
mock_original_toc_copy = "tests/testdata/mock-java-original-toc-copy.yml"
mock_updated_toc = "tests/testdata/mock-java-updated-toc.yml"


class PrepareDocsTest(unittest.TestCase):
    def setUp(cls):
        # assure mock and updated are not the same before
        assert (
            filecmp.cmp(mock_original_toc, mock_updated_toc, shallow=False)
        ) is False

        # make a copy of the original since script will update original file
        shutil.copyfile(mock_original_toc, mock_original_toc_copy)
        prepare_toc(mock_original_toc, "google-cloud-testing")

    def tearDown(cls):
        # overwrite changes to original from copy
        shutil.move(mock_original_toc_copy, mock_original_toc)

    def test_original_is_updated(self):
        assert (filecmp.cmp(mock_original_toc, mock_updated_toc, shallow=False)) is True

    def test_original_not_copy(self):
        assert (
            filecmp.cmp(mock_original_toc, mock_original_toc_copy, shallow=False)
        ) is False

    def test_original_valid_yaml(self):
        with open(mock_original_toc, "r") as stream:
            try:
                yaml.safe_load(stream)
            except yaml.YAMLError:
                pytest.fail(f"unable to parse YAML: {mock_original_toc}")
