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

from synthtool.gcp.common import decamelize
from pathlib import Path
from pytest import raises
import os
import synthtool as s
import tempfile
import shutil

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
    with tempfile.TemporaryDirectory() as tempdir:
        workdir = shutil.copytree(path_to_gen, Path(tempdir) / "client_library")
        cwd = os.getcwd()
        os.chdir(workdir)

        try:
            sample_files = common.py_samples(
                unit_cov_level=97, cov_level=99, samples=True
            )
            s.move(sample_files, excludes=["noxfile.py"])
            assert os.path.isfile(workdir / "samples" / "README.md")
        finally:
            os.chdir(cwd)


def test_py_samples_custom_path():
    path_to_gen = MOCK / "custom_path"
    with tempfile.TemporaryDirectory() as tempdir:
        workdir = shutil.copytree(path_to_gen, Path(tempdir) / "custom_path")
        cwd = os.getcwd()
        os.chdir(workdir)

        try:
            sample_files = common.py_samples(
                unit_cov_level=97, cov_level=99, samples=True
            )
            s.move(sample_files, excludes=["noxfile.py"])
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
                sample_files = common.py_samples(
                    unit_cov_level=97, cov_level=99, samples=True
                )
                s.move(sample_files, excludes=["noxfile.py"])
                assert "'nonexistent_folder' does not exist" in str(e.value)
        finally:
            os.chdir(cwd)


def test_py_samples_samples_folder():
    path_to_gen = MOCK / "samples_folder"
    with tempfile.TemporaryDirectory() as tempdir:
        workdir = shutil.copytree(path_to_gen, Path(tempdir) / "samples_folder")
        cwd = os.getcwd()
        os.chdir(workdir)

        try:
            sample_files = common.py_samples(
                unit_cov_level=97, cov_level=99, samples=True
            )
            s.move(sample_files, excludes=["noxfile.py"])
            assert os.path.isfile(workdir / "README.md")
        finally:
            os.chdir(cwd)

def test_py_samples_override():
    path_to_gen = MOCK / "override_path"
    with tempfile.TemporaryDirectory() as tempdir:
        workdir = shutil.copytree(path_to_gen, Path(tempdir) / "override_path")
        cwd = os.getcwd()
        os.chdir(workdir)

        try:
            sample_files = common.py_samples(
                unit_cov_level=97, cov_level=99, samples=True
            )
            for path in sample_files:
                s.move(path, excludes=['noxfile.py'])
            assert os.path.isfile(workdir / "README.md")
            assert os.path.isfile(workdir / "override" / "README.md")
        finally:
            os.chdir(cwd)

def test_py_samples_override_content():
    path_to_gen = MOCK / "override_path"
    with tempfile.TemporaryDirectory() as tempdir:
        workdir = shutil.copytree(path_to_gen, Path(tempdir) / "override_path")
        cwd = os.getcwd()
        os.chdir(workdir)

        try:
            sample_files = common.py_samples(
                unit_cov_level=97, cov_level=99, samples=True
            )
            for path in sample_files:
                s.move(path, excludes=['noxfile.py'])
            os.chdir(workdir)
            with open('README.md') as f:
                result = f.read()
                assert "Hello World" in result
                assert "Quickstart" not in result
            os.chdir(workdir / "override")
            with open('README.md') as f:
                result = f.read()
                assert "Hello World" not in result
                assert "Quickstart"  in result
        finally:
            os.chdir(cwd)

def test_py_samples_multiple_override():
    path_to_gen = MOCK / "multiple_override_path"
    with tempfile.TemporaryDirectory() as tempdir:
        workdir = shutil.copytree(path_to_gen, Path(tempdir) / "multiple_override_path")
        cwd = os.getcwd()
        os.chdir(workdir)

        try:
            sample_files = common.py_samples(
                unit_cov_level=97, cov_level=99, samples=True
            )
            print(sample_files)
            for path in sample_files:
                s.move(path, excludes=['noxfile.py'])
            assert os.path.isfile(workdir / "README.md")
            assert os.path.isfile(workdir / "override" / "README.md")
            assert os.path.isfile(workdir / "another_override" / "README.md")
            os.chdir(workdir / "another_override")
            with open('README.md') as f:
                result = f.read()
                print(result)
                assert "Hello World" in result
                assert "Hello AGAIN"  in result
        finally:
            os.chdir(cwd)
