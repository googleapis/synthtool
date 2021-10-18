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


from filecmp import dircmp
import os
from pathlib import Path
import shutil

import pytest

from synthtool.languages import php


FIXTURES = Path(__file__).parent / "fixtures" / "php"


@pytest.fixture(scope="function", params=["php_asset"])
def copy_fixture(request, tmp_path):
    """A fixture for preparing test data.
    """
    param = request.param
    test_dir = tmp_path / param

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


def test_owlbot_php(copy_fixture):
    entries = os.scandir(copy_fixture)

    with php.pushd(copy_fixture / "src"):
        php.owlbot_entrypoint()

    dcmp = dircmp(copy_fixture / "expected", copy_fixture / "src")
    diff_string = get_diff_string(dcmp, "")
    assert diff_string == ""
