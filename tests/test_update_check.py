# Copyright 2026 Google LLC
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

import importlib
import sys
from unittest import mock

import pytest


@pytest.mark.parametrize("module", ["synthtool.__main__", "synthtool.update_check"])
def test_import_without_pkg_resources(module):
    # setuptools >= 82 no longer ships `pkg_resources`.
    with mock.patch.dict(sys.modules, {"pkg_resources": None}):
        sys.modules.pop(module, None)
        importlib.import_module(module)


def test_check_for_updates_without_pkg_resources(tmp_path):
    with mock.patch.dict(sys.modules, {"pkg_resources": None}):
        sys.modules.pop("synthtool.update_check", None)
        update_check = importlib.import_module("synthtool.update_check")
        messages = []
        with mock.patch.object(update_check, "_only_once_pls", return_value=True):
            with mock.patch.object(
                update_check, "_get_pypi_version", return_value="999.0.0"
            ):
                update_check.check_for_updates("pytest", print=messages.append)
    assert "newer version available" in messages[0]
