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
import pathlib
import filecmp
import pytest

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


def test_extract_clients_no_file():
    index_ts_path = pathlib.Path(
        FIXTURES / "node_templates" / "index_samples" / "no_exist_index.ts"
    )

    with pytest.raises(FileNotFoundError) as err_msg:
        clients = node.extract_clients(index_ts_path)
        assert not clients
        assert f"Failed to find {index_ts_path}" in err_msg


def test_extract_single_clients():
    index_ts_path = pathlib.Path(
        FIXTURES / "node_templates" / "index_samples" / "single_index.ts"
    )

    clients = node.extract_clients(index_ts_path)

    assert len(clients) == 1
    assert clients[0] == "TextToSpeechClient"


def test_extract_multiple_clients():
    index_ts_path = pathlib.Path(
        FIXTURES / "node_templates" / "index_samples" / "multiple_index.ts"
    )

    clients = node.extract_clients(index_ts_path)

    assert len(clients) == 2
    assert clients[0] == "StreamingVideoIntelligenceServiceClient"
    assert clients[1] == "VideoIntelligenceServiceClient"


def test_generate_index_ts():
    cwd = os.getcwd()
    # use a non-nodejs template directory
    os.chdir(FIXTURES / "node_templates" / "index_samples")
    isGen = node.generate_index_ts(["v1", "v1beta1"], "v1")
    generated_index_path = pathlib.Path(
        FIXTURES / "node_templates" / "index_samples" / "src" / "index.ts"
    )
    sample_index_path = pathlib.Path(
        FIXTURES / "node_templates" / "index_samples" / "sample_index.ts"
    )

    assert isGen is True
    assert filecmp.cmp(generated_index_path, sample_index_path)
    os.chdir(cwd)


def test_generate_index_ts_empty_versions():
    cwd = os.getcwd()
    # use a non-nodejs template directory
    os.chdir(FIXTURES / "node_templates" / "index_samples")

    with pytest.raises(AttributeError) as err:
        _ = node.generate_index_ts([], "v1")
        assert "can't be empty" in err.args

    os.chdir(cwd)


def test_generate_index_ts_invalid_default_version():
    cwd = os.getcwd()
    # use a non-nodejs template directory
    os.chdir(FIXTURES / "node_templates" / "index_samples")
    versions = ["v1beta1"]
    default_version = "v1"

    with pytest.raises(AttributeError) as err:
        _ = node.generate_index_ts(versions, default_version)
        assert f"must contain default version {default_version}" in err.args

    os.chdir(cwd)


def test_generate_index_ts_no_clients():
    cwd = os.getcwd()
    # use a non-nodejs template directory
    os.chdir(FIXTURES / "node_templates" / "index_samples")
    versions = ["v1", "v1beta1", "invalid_index"]
    default_version = "invalid_index"

    # with pytest.raises(AttributeError) as err:
    isGen = node.generate_index_ts(versions, default_version)
    # assert f"No client is exported in the default version's({default_version}) index.ts ." in err.args
    assert isGen is False

    os.chdir(cwd)


class TestPostprocess(TestCase):
    @patch("synthtool.shell.run")
    def test_install(self, shell_run_mock):
        node.install()
        calls = shell_run_mock.call_args_list
        assert any(["npm install" in " ".join(call[0][0]) for call in calls])

    @patch("synthtool.shell.run")
    def test_fix(self, shell_run_mock):
        node.fix()
        calls = shell_run_mock.call_args_list
        assert any(["npm run fix" in " ".join(call[0][0]) for call in calls])

    @patch("synthtool.shell.run")
    def test_compile_protos(self, shell_run_mock):
        node.compile_protos()
        calls = shell_run_mock.call_args_list
        assert any(["npx compileProtos src" in " ".join(call[0][0]) for call in calls])

    @patch("synthtool.shell.run")
    def test_postprocess_gapic_library(self, shell_run_mock):
        node.postprocess_gapic_library()
        calls = shell_run_mock.call_args_list
        assert any(["npm install" in " ".join(call[0][0]) for call in calls])
        assert any(["npm run fix" in " ".join(call[0][0]) for call in calls])
        assert any(["npx compileProtos src" in " ".join(call[0][0]) for call in calls])
