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

from unittest import TestCase
from unittest.mock import patch
import os
from pathlib import Path
from synthtool.languages import node

FIXTURES = Path(__file__).parent / "fixtures"


def test_quickstart_metadata_with_snippet():
    cwd = os.getcwd()
    os.chdir(FIXTURES / "node_templates" / "standard")

    metadata = node.template_metadata()

    # should have loaded the special quickstart sample (ignoring header).
    assert "ID of the Cloud Bigtable instance" in metadata["quickstart"]
    assert "limitations under the License" not in metadata["quickstart"]

    assert isinstance(metadata["samples"], list)

    # should have a link to the quickstart in the samples
    sample_names = list(map(lambda sample: sample["file"], metadata["samples"]))
    assert "samples/quickstart.js" in sample_names

    os.chdir(cwd)


def test_quickstart_metadata_without_snippet():
    cwd = os.getcwd()
    os.chdir(FIXTURES / "node_templates" / "no_quickstart_snippet")

    metadata = node.template_metadata()

    # should not have populated the quickstart for the README
    assert not metadata["quickstart"]

    assert isinstance(metadata["samples"], list)

    # should not have a link to the quickstart in the samples
    sample_names = list(map(lambda sample: sample["file"], metadata["samples"]))
    assert "samples/quickstart.js" not in sample_names

    os.chdir(cwd)


def test_no_samples():
    cwd = os.getcwd()
    # use a non-nodejs template directory
    os.chdir(FIXTURES)

    metadata = node.template_metadata()

    # should not have populated the quickstart for the README
    assert not metadata["quickstart"]

    assert isinstance(metadata["samples"], list)
    assert len(metadata["samples"]) == 0

    os.chdir(cwd)


class TestPostprocess(TestCase):
    def test_is_gapic_library_gapic(self):
        cwd = os.getcwd()
        os.chdir(FIXTURES / "node_postprocess" / "gapic")
        result = node.is_gapic_library()
        os.chdir(cwd)
        assert result is True

    def test_is_gapic_library_nongapic1(self):
        cwd = os.getcwd()
        os.chdir(FIXTURES / "node_postprocess" / "nongapic1")
        result = node.is_gapic_library()
        os.chdir(cwd)
        assert result is False

    def test_is_gapic_library_nongapic2(self):
        cwd = os.getcwd()
        os.chdir(FIXTURES / "node_postprocess" / "nongapic2")
        result = node.is_gapic_library()
        os.chdir(cwd)
        assert result is False

    def test_is_gapic_library_nongapic3(self):
        cwd = os.getcwd()
        os.chdir(FIXTURES / "node_postprocess" / "nongapic3")
        result = node.is_gapic_library()
        os.chdir(cwd)
        assert result is False

    @patch("synthtool.shell.run")
    def test_does_not_run_compile_protos_for_nongapic(self, shell_run_mock):
        cwd = os.getcwd()
        os.chdir(FIXTURES / "node_postprocess" / "nongapic1")
        node.postprocess()
        os.chdir(cwd)
        calls = shell_run_mock.call_args_list
        assert len(calls) > 0
        for call in calls:
            assert "compileProtos" not in call[0][0]

    @patch("synthtool.shell.run")
    def test_runs_compile_protos_for_gapic(self, shell_run_mock):
        cwd = os.getcwd()
        os.chdir(FIXTURES / "node_postprocess" / "gapic")
        node.postprocess()
        os.chdir(cwd)
        calls = shell_run_mock.call_args_list
        ok = False
        for call in calls:
            if "compileProtos" in call[0][0]:
                ok = True
        assert ok
