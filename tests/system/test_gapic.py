# Copyright 2018 Google LLC
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
# limitations under the License.import synthtool

import pathlib
import subprocess
import sys

import pytest


HERE = pathlib.Path(__file__).parent
FIXTURES = HERE / "fixtures"


@pytest.fixture
def tmpcwd(tmpdir):
    """Uses a temporary directory as the current working directory."""
    with tmpdir.as_cwd():
        yield tmpdir


def copy_synth_file(source):
    synth_file_source = (FIXTURES / source).read_text()
    pathlib.Path("./synth.py").write_text(synth_file_source)


@pytest.mark.parametrize(
    ["synth_file", "expected_file"],
    [
        ("gapic-basic-python.synth.py", "setup.py"),
        ("gapic-basic-node.synth.py", "package.json"),
    ],
)
def test_basic(tmpcwd, synth_file, expected_file):
    copy_synth_file(synth_file)

    subprocess.check_call([sys.executable, "-m", "synthtool", "synth.py"])

    assert (tmpcwd / "synth.metadata").exists()
    assert (tmpcwd / expected_file).exists()
