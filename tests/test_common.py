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

MOCK = Path(__file__).parent / "generationmock"
common = s.gcp.CommonTemplates()

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
    os.chdir(path_to_gen)
    sample_files = common.py_samples(unit_cov_level=97, cov_level=99, samples=True)
    s.move(sample_files, excludes=['noxfile.py'])
    assert os.path.isfile(path_to_gen / "samples" / "README.md")
    os.remove(path_to_gen / "samples" / "README.md")

def test_py_samples_custom_path():
    path_to_gen = MOCK / "custom_path"
    os.chdir(path_to_gen)
    sample_files = common.py_samples(unit_cov_level=97, cov_level=99, samples=True)
    s.move(sample_files, excludes=['noxfile.py'])
    assert os.path.isfile(path_to_gen / "custom_samples_folder" / "README.md")
    os.remove(path_to_gen / "custom_samples_folder" / "README.md")

def test_py_samples_custom_path_DNE():
    with raises(Exception) as e:
        os.chdir(MOCK / "custom_path_DNE")
        sample_files = common.py_samples(unit_cov_level=97, cov_level=99, samples=True)
        s.move(sample_files, excludes=['noxfile.py'])
        assert "'nonexistent_folder' does not exist" in str(e.value)

def test_py_samples_samples_folder():
    path_to_gen = MOCK / "samples_folder"
    os.chdir(path_to_gen)
    sample_files = common.py_samples(unit_cov_level=97, cov_level=99, samples=True)
    s.move(sample_files, excludes=['noxfile.py'])
    assert os.path.isfile(path_to_gen / "README.md")
    os.remove(path_to_gen / "README.md")
