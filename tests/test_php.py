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
import shutil
import tempfile

import pytest

from synthtool.languages import php


FIXTURES = Path(__file__).parent / "fixtures" / "php"


@pytest.fixture(scope="session")
def hybrid_tmp_path():
    """A tmp dir implementation both for local run and on Kokoro."""
    # Trampoline mount KOKORO_ROOT at the same path.
    # So we can mount files under there with docker in docker.
    hybrid_dir = os.environ.get("KOKORO_ROOT", None)
    d = tempfile.mkdtemp(prefix="synthtool-php-test", dir=hybrid_dir)

    yield d

    shutil.rmtree(d)


@pytest.fixture(scope="function", params=["php_asset"])
def copy_fixture(request, hybrid_tmp_path):
    """A fixture for preparing test data."""
    param = request.param
    test_dir = Path(f"{hybrid_tmp_path}/{param}")

    shutil.copytree(FIXTURES / param, test_dir)
    print(f"Copied fixture to {test_dir}")

    yield test_dir

    shutil.rmtree(test_dir)


def get_diff_string(dcmp, buf=""):
    for name in dcmp.diff_files:
        buf += f"diff_file: {name} found in {dcmp.left} and {dcmp.right}\n"
    for sub_dcmp in dcmp.subdirs.values():
        buf += get_diff_string(sub_dcmp)
    return buf


def test_find_copy_target_direct(tmp_path: Path):
    (tmp_path / "V1").mkdir()
    assert php._find_copy_target(tmp_path, "v1") == tmp_path


def test_find_copy_target_in_sibling(tmp_path: Path):
    sibling_empty = tmp_path / "sibling_empty"
    sibling_empty.mkdir()

    sibling_other = tmp_path / "sibling_other"
    sibling_other.mkdir()
    (sibling_other / "v2").mkdir()

    sibling_match = tmp_path / "sibling_match"
    sibling_match.mkdir()
    (sibling_match / "V1").mkdir()

    assert php._find_copy_target(tmp_path, "v1") == sibling_match


def test_find_copy_target_nested(tmp_path: Path):
    nested_dir = tmp_path / "a" / "b"
    nested_dir.mkdir(parents=True)
    (nested_dir / "v1beta1").mkdir()

    assert php._find_copy_target(tmp_path, "v1beta1") == nested_dir


def test_find_copy_target_not_found(tmp_path: Path):
    nested_dir = tmp_path / "a" / "b"
    nested_dir.mkdir(parents=True)
    (nested_dir / "v2").mkdir()

    assert php._find_copy_target(tmp_path, "v1") is None


def test_find_copy_target_empty_dir(tmp_path: Path):
    assert php._find_copy_target(tmp_path, "v1") is None
