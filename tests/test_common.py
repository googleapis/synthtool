# Copyright 2019 Google LLC
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

import json
import os
import tempfile
from pathlib import Path
from unittest import mock

from pytest import raises

import synthtool as s
from synthtool.gcp.common import _get_default_branch_name, decamelize, detect_versions

from . import util

MOCK = Path(__file__).parent / "generationmock"
template_dir = Path(__file__).parent.parent / "synthtool/gcp/templates"
common = s.gcp.CommonTemplates(template_path=template_dir)


def test_converts_camel_to_title():
    assert decamelize("fooBar") == "Foo Bar"
    assert decamelize("fooBarSnuh") == "Foo Bar Snuh"


def test_handles_acronym():
    assert decamelize("ACL") == "ACL"
    assert decamelize("coolACL") == "Cool ACL"
    assert decamelize("loadJSONFromGCS") == "Load JSON From GCS"


def test_handles_empty_string():
    assert decamelize(None) == ""
    assert decamelize("") == ""


def test_get_default_branch():
    with mock.patch.dict(os.environ, {"DEFAULT_BRANCH": "chickens"}):
        assert _get_default_branch_name("repo_name") == "chickens"


def test_get_default_branch_path():
    f = tempfile.NamedTemporaryFile("wt", delete=False)
    fname = f.name
    f.write("ducks\n")
    f.close()
    with mock.patch.dict(os.environ, {"DEFAULT_BRANCH_PATH": fname}):
        assert _get_default_branch_name("repo_name") == "ducks"


def test_py_samples_clientlib():
    path_to_gen = MOCK / "client_library"
    with util.copied_fixtures_dir(path_to_gen) as workdir:
        sample_files = common.py_samples(unit_cov_level=97, cov_level=99, samples=True)
        s.move(sample_files, excludes=["noxfile.py"])
        assert os.path.isfile(workdir / "samples" / "README.md")


def test_py_samples_custom_path():
    path_to_gen = MOCK / "custom_path"
    with util.copied_fixtures_dir(path_to_gen) as workdir:
        sample_files = common.py_samples(unit_cov_level=97, cov_level=99, samples=True)
        s.move(sample_files, excludes=["noxfile.py"])
        assert os.path.isfile(workdir / "custom_samples_folder" / "README.md")


def test_py_samples_custom_path_DNE():
    path_to_gen = MOCK / "custom_path_DNE"
    with util.copied_fixtures_dir(path_to_gen) as workdir:
        with raises(Exception) as e:
            os.chdir(workdir / "custom_path_DNE")
            sample_files = common.py_samples(
                unit_cov_level=97, cov_level=99, samples=True
            )
            s.move(sample_files, excludes=["noxfile.py"])
            assert "'nonexistent_folder' does not exist" in str(e.value)


def test_py_samples_samples_folder():
    path_to_gen = MOCK / "samples_folder"
    with util.copied_fixtures_dir(path_to_gen) as workdir:
        sample_files = common.py_samples(unit_cov_level=97, cov_level=99, samples=True)
        s.move(sample_files, excludes=["noxfile.py"])
        assert os.path.isfile(workdir / "README.md")


def test_py_samples_override():
    path_to_gen = MOCK / "override_path"
    with util.copied_fixtures_dir(path_to_gen) as workdir:
        sample_files = common.py_samples(unit_cov_level=97, cov_level=99, samples=True)
        for path in sample_files:
            s.move(path, excludes=["noxfile.py"])
        assert os.path.isfile(workdir / "README.md")
        assert os.path.isfile(workdir / "override" / "README.md")


def test_py_samples_override_content():
    path_to_gen = MOCK / "override_path"
    with util.copied_fixtures_dir(path_to_gen) as workdir:
        sample_files = common.py_samples(unit_cov_level=97, cov_level=99, samples=True)
        for path in sample_files:
            s.move(path, excludes=["noxfile.py"])
        os.chdir(workdir)
        with open("README.md") as f:
            result = f.read()
            assert "Hello World" in result
            assert "Quickstart" not in result
        os.chdir(workdir / "override")
        with open("README.md") as f:
            result = f.read()
            assert "Hello World" not in result
            assert "Quickstart" in result


def test_py_samples_multiple_override():
    path_to_gen = MOCK / "multiple_override_path"
    with util.copied_fixtures_dir(path_to_gen) as workdir:
        sample_files = common.py_samples(unit_cov_level=97, cov_level=99, samples=True)
        for path in sample_files:
            s.move(path, excludes=["noxfile.py"])
        assert os.path.isfile(workdir / "README.md")
        assert os.path.isfile(workdir / "override" / "README.md")
        assert os.path.isfile(workdir / "another_override" / "README.md")
        os.chdir(workdir / "another_override")
        with open("README.md") as f:
            result = f.read()
            assert "Hello World" in result
            assert "Hello Synthtool" in result


def test_py_samples_multiple_override_content():
    path_to_gen = MOCK / "multiple_override_path"
    with util.copied_fixtures_dir(path_to_gen) as workdir:
        sample_files = common.py_samples(unit_cov_level=97, cov_level=99, samples=True)
        for path in sample_files:
            s.move(path, excludes=["noxfile.py"])
        os.chdir(workdir / "override")
        with open("README.md") as f:
            result = f.read()
            assert "Quickstart" in result
            assert "first_arg" in result
        os.chdir(workdir / "another_override")
        with open("README.md") as f:
            result = f.read()
            assert "Hello World" in result
            assert "Hello Synthtool" in result
        os.chdir(workdir)
        with open("README.md") as f:
            result = f.read()
            assert "Last Example" in result


def test_detect_versions_src():
    temp_dir = Path(tempfile.mkdtemp())
    src_dir = temp_dir / "src"
    for v in ("v1", "v2", "v3"):
        os.makedirs(src_dir / v)

    with util.chdir(temp_dir):
        versions = detect_versions()
        assert ["v1", "v2", "v3"] == versions


def test_detect_versions_staging():
    temp_dir = Path(tempfile.mkdtemp())
    staging_dir = temp_dir / "owl-bot-staging"
    for v in ("v1", "v2", "v3"):
        os.makedirs(staging_dir / v)

    versions = detect_versions(staging_dir)
    assert ["v1", "v2", "v3"] == versions


def test_detect_versions_dir_not_found():
    temp_dir = Path(tempfile.mkdtemp())

    versions = detect_versions(temp_dir / "does-not-exist")
    assert [] == versions


def test_detect_versions_with_default_version():
    temp_dir = Path(tempfile.mkdtemp())
    src_dir = temp_dir / "src"
    vs = ("v1", "v2", "v3")
    for v in vs:
        os.makedirs(src_dir / v)

    with util.chdir(temp_dir):
        versions = detect_versions(default_version="v1")
        assert ["v2", "v3", "v1"] == versions
        versions = detect_versions(default_version="v2")
        assert ["v1", "v3", "v2"] == versions
        versions = detect_versions(default_version="v3")
        assert ["v1", "v2", "v3"] == versions


def test_detect_versions_with_default_version_from_metadata():
    temp_dir = Path(tempfile.mkdtemp())
    default_dir = temp_dir / "src"
    for v in ("api_v1", "api_v2", "api_v3"):
        os.makedirs(default_dir / v)

    with util.chdir(temp_dir):
        # Set default_version to "api_v1"
        test_json = {"default_version": "api_v1"}
        with open(".repo-metadata.json", "w") as metadata:
            json.dump(test_json, metadata)
        versions = detect_versions(default_first=True)
        assert ["api_v1", "api_v2", "api_v3"] == versions

        # Set default_version to "api_v2"
        test_json = {"default_version": "api_v2"}
        with open(".repo-metadata.json", "w") as metadata:
            json.dump(test_json, metadata)
        versions = detect_versions(default_first=True)
        assert ["api_v2", "api_v1", "api_v3"] == versions

        # Set default_version to "api_v3"
        test_json = {"default_version": "api_v3"}
        with open(".repo-metadata.json", "w") as metadata:
            json.dump(test_json, metadata)
        versions = detect_versions(default_first=True)
        assert ["api_v3", "api_v1", "api_v2"] == versions


def test_detect_versions_nested_directory():
    temp_dir = Path(tempfile.mkdtemp())
    src_dir = temp_dir / "src" / "src2" / "src3" / "src4"
    vs = ("v1", "v2", "v3")
    for v in vs:
        os.makedirs(src_dir / v)
        # this folder should be ignored
        os.makedirs(src_dir / v / "some_other_service_v1_beta")

    with util.chdir(temp_dir):
        versions = detect_versions(default_version="v1")
        assert ["v2", "v3", "v1"] == versions
        versions = detect_versions(default_version="v2")
        assert ["v1", "v3", "v2"] == versions
        versions = detect_versions(default_version="v3")
        assert ["v1", "v2", "v3"] == versions
