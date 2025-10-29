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

import os
from pathlib import Path
import yaml

import pytest

from synthtool import gcp
from synthtool.sources import templates
from . import util


PYTHON_LIBRARY = Path(__file__).parent.parent / "synthtool/gcp/templates/python_library"


def test_library_codeowners():
    t = templates.Templates(PYTHON_LIBRARY / ".github")
    result = t.render(
        "CODEOWNERS",
        metadata={"repo": {"codeowner_team": "googleapis/foo"}},
    ).read_text()
    assert "*     @googleapis/yoshi-python googleapis/foo" in result
    assert "/samples/   @googleapis/python-samples-reviewers googleapis/foo" in result


def test_library_codeowners_without_metadata():
    t = templates.Templates(PYTHON_LIBRARY / ".github")
    result = t.render(
        "CODEOWNERS",
        metadata={"repo": {}},
    ).read_text()
    assert "*     @googleapis/yoshi-python" in result
    assert "/samples/   @googleapis/python-samples-reviewers" in result
    assert "@googleapis/foo" not in result


def assert_valid_yaml(file):
    with open(file, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError:
            pytest.fail(f"unable to parse YAML: {file}")


def test_library_blunderbuss_single_codeowner():
    t = templates.Templates(PYTHON_LIBRARY / ".github")
    result = t.render(
        "blunderbuss.yml",
        metadata={"repo": {"codeowner_team": "googleapis/foo"}},
    ).read_text()
    try:
        config = yaml.safe_load(result)
        assert "googleapis/python-core-client-libraries" not in config["assign_issues"]
        assert "googleapis/foo" in config["assign_issues"]
        assert "googleapis/foo" in config["assign_prs"]
        assert (
            "googleapis/python-samples-reviewers" in config["assign_issues_by"][0]["to"]
        )
        assert "googleapis/foo" in config["assign_issues_by"][0]["to"]
    except yaml.YAMLError:
        pytest.fail(f"unable to parse YAML: {result}")


def test_library_blunderbuss_multiple_codeowner():
    t = templates.Templates(PYTHON_LIBRARY / ".github")
    result = t.render(
        "blunderbuss.yml",
        metadata={"repo": {"codeowner_team": "googleapis/foo googleapis/bar"}},
    ).read_text()
    try:
        config = yaml.safe_load(result)
        assert "googleapis/python-core-client-libraries" not in config["assign_issues"]
        assert "googleapis/foo" in config["assign_issues"]
        assert "googleapis/bar" in config["assign_issues"]
        assert "googleapis/foo" in config["assign_prs"]
        assert "googleapis/bar" in config["assign_prs"]
        assert (
            "googleapis/python-samples-reviewers" in config["assign_issues_by"][0]["to"]
        )
        assert "googleapis/foo" in config["assign_issues_by"][0]["to"]
        assert "googleapis/bar" in config["assign_issues_by"][0]["to"]
    except yaml.YAMLError:
        pytest.fail(f"unable to parse YAML: {result}")


def test_library_blunderbuss_no_codeowner():
    t = templates.Templates(PYTHON_LIBRARY / ".github")
    result = t.render(
        "blunderbuss.yml",
        metadata={"repo": {}},
    ).read_text()
    try:
        config = yaml.safe_load(result)
        assert "googleapis/python-core-client-libraries" in config["assign_issues"]
        assert "googleapis/foo" not in config["assign_issues"]
        assert (
            "googleapis/python-samples-reviewers" in config["assign_issues_by"][0]["to"]
        )
        assert "googleapis/foo" not in config["assign_issues_by"][0]["to"]
    except yaml.YAMLError:
        pytest.fail(f"unable to parse YAML: {result}")


def test_python_library():
    with util.chdir(Path(__file__).parent / "fixtures/python_library"):
        template_dir = Path(__file__).parent.parent / "synthtool/gcp/templates"
        common = gcp.CommonTemplates(template_path=template_dir)
        templated_files = common.py_library()

        assert os.path.exists(templated_files / ".kokoro/build.sh")


def test_split_system_tests():
    with util.chdir(Path(__file__).parent / "fixtures/python_library"):
        template_dir = Path(__file__).parent.parent / "synthtool/gcp/templates"
        common = gcp.CommonTemplates(template_path=template_dir)
        templated_files = common.py_library(split_system_tests=True)

        with open(templated_files / ".kokoro/presubmit/presubmit.cfg", "r") as f:
            contents = f.read()
            assert "RUN_SYSTEM_TESTS" in contents
            assert "false" in contents

        assert os.path.exists(templated_files / ".kokoro/presubmit/system-3.8.cfg")
        with open(templated_files / ".kokoro/presubmit/system-3.8.cfg", "r") as f:
            contents = f.read()
            assert "system-3.8" in contents
