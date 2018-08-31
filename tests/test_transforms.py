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
# limitations under the License.

import os
import stat
from pathlib import Path

import pytest

from synthtool import transforms
from synthtool import _tracked_paths


@pytest.fixture()
def expand_path_fixtures(tmpdir):
    files = ["a.txt", "b.py", "c.md", "dira/e.txt", "dira/f.py", "dirb/suba/g.py"]

    for file in files:
        path = tmpdir.join(file)
        path.write_text("content", encoding="utf-8", ensure=True)

    cwd = os.getcwd()
    os.chdir(str(tmpdir))
    yield tmpdir
    os.chdir(cwd)


@pytest.fixture()
def executable_fixtures(tmpdir):
    # Executable file
    executable = "exec.sh"
    path = tmpdir.join(executable)
    path.write_text("content", encoding="utf-8", ensure=True)
    path.chmod(0o100775)

    cwd = os.getcwd()
    os.chdir(str(tmpdir))
    yield tmpdir
    os.chdir(cwd)


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        ("a.txt", ["a.txt"]),
        ("*", ["a.txt", "b.py", "c.md", "dira", "dirb"]),
        ("*.py", ["b.py"]),
        ("**/*.py", ["b.py", "dira/f.py", "dirb/suba/g.py"]),
        (
            "**/*",
            [
                "a.txt",
                "b.py",
                "c.md",
                "dira",
                "dira/e.txt",
                "dira/f.py",
                "dirb",
                "dirb/suba",
                "dirb/suba/g.py",
            ],
        ),
    ],
)
def test__expand_paths(expand_path_fixtures, input, expected):
    paths = sorted([str(x) for x in transforms._expand_paths(input)])
    assert paths == expected


@pytest.mark.parametrize(
    ["input", "expected"],
    [("e.txt", ["dira/e.txt"]), ("*", ["dira/e.txt", "dira/f.py"])],
)
def test__expand_paths_with_root(expand_path_fixtures, input, expected):
    paths = sorted([str(x) for x in transforms._expand_paths(input, root="dira")])
    assert paths == expected


def test__filter_files(expand_path_fixtures):
    files = sorted(
        [str(x) for x in transforms._filter_files(transforms._expand_paths("**/*"))]
    )

    assert files == [
        "a.txt",
        "b.py",
        "c.md",
        "dira/e.txt",
        "dira/f.py",
        "dirb/suba/g.py",
    ]


def test__file_copy_mode(executable_fixtures):
    executable = "exec.sh"
    destination = executable_fixtures / "exec_copy.sh"

    transforms.move([executable], destination)

    assert destination.stat().mode & stat.S_IXUSR


def test__move_to_dest(expand_path_fixtures):
    tmp_path = Path(str(expand_path_fixtures))
    _tracked_paths.add(expand_path_fixtures)
    dest = Path(str(expand_path_fixtures / "dest"))

    transforms.move(tmp_path, dest, excludes=["dira/f.py"])

    files = sorted([str(x) for x in transforms._expand_paths("**/*", root="dest")])

    # Assert destination does not contain dira/e.py (excluded)
    assert files == [
        "dest/a.txt",
        "dest/b.py",
        "dest/c.md",
        "dest/dira",
        "dest/dira/e.txt",
        "dest/dirb",
        "dest/dirb/suba",
        "dest/dirb/suba/g.py",
    ]
