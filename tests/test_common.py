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

from synthtool.gcp.common import decamelize, CommonTemplates
from pathlib import Path
from pytest import raises
import os
import synthtool as s
import tempfile
import shutil

MOCK = Path(__file__).parent / "generationmock"
common = s.gcp.CommonTemplates()
meta = { "repo" : {
    "name": "bigtable",
    "name_pretty": "Cloud Bigtable",
    "product_documentation": "https://cloud.google.com/bigtable",
    "client_documentation": "https://googleapis.dev/python/bigtable/latest",
    "issue_tracker": "https://issuetracker.google.com/savedsearches/559777",
    "release_level": "ga",
    "language": "python",
    "repo": "googleapis/python-bigtable",
    "distribution_name": "google-cloud-bigtable",
    "api_id": "bigtable.googleapis.com",
    "requires_billing": True,
    "client_library": True,
    "sample_project_dir": "custom_samples_folder",
    "samples": [
              {"name": "Quickstart",
              "description": "Example sample for product",
              "file": "quickstart.py",
              "custom_content": "This is custom text for the sample",
              "runnable": "True"},
              {"name": "Hello World",
              "description": "Example beginner application",
              "file": "main.py"}
    ]}
}

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

def test_py_samples_clientlib():
    path_to_gen = MOCK / "client_library"
    with tempfile.TemporaryDirectory() as tempdir:
        workdir = shutil.copytree(
            path_to_gen, Path(tempdir) / "client_library"
        )
        cwd = os.getcwd()
        os.chdir(workdir)

        try:
            sample_files = common.py_samples(unit_cov_level=97, cov_level=99, samples=True)
            s.move(sample_files, excludes=['noxfile.py'])
            assert os.path.isfile(workdir / "samples" / "README.md")
        finally:
            os.chdir(cwd)

def test_py_samples_custom_path():
    path_to_gen = MOCK / "custom_path"
    with tempfile.TemporaryDirectory() as tempdir:
        workdir = shutil.copytree(
            path_to_gen, Path(tempdir) / "custom_path"
        )
        cwd = os.getcwd()
        os.chdir(workdir)

        try:
            sample_files = common.py_samples(unit_cov_level=97, cov_level=99, samples=True)
            s.move(sample_files, excludes=['noxfile.py'])
            assert os.path.isfile(workdir / "custom_samples_folder" / "README.md")
        finally:
            os.chdir(cwd)

def test_py_samples_custom_path_DNE():
    with tempfile.TemporaryDirectory() as tempdir:
        workdir = shutil.copytree(
            MOCK / "custom_path_DNE", Path(tempdir) / "custom_path_DNE"
        )
        cwd = os.getcwd()
        os.chdir(workdir)

        try:
            with raises(Exception) as e:
                os.chdir(workdir / "custom_path_DNE")
                sample_files = common.py_samples(unit_cov_level=97, cov_level=99, samples=True)
                s.move(sample_files, excludes=['noxfile.py'])
                assert "'nonexistent_folder' does not exist" in str(e.value)
        finally:
            os.chdir(cwd)

def test_py_samples_samples_folder():
    path_to_gen = MOCK / "samples_folder"
    with tempfile.TemporaryDirectory() as tempdir:
        workdir = shutil.copytree(
            path_to_gen, Path(tempdir) / "samples_folder"
        )
        cwd = os.getcwd()
        os.chdir(workdir)

        try:
            sample_files = common.py_samples(unit_cov_level=97, cov_level=99, samples=True)
            s.move(sample_files, excludes=['noxfile.py'])
            assert os.path.isfile(workdir / "README.md")
        finally:
            os.chdir(cwd)