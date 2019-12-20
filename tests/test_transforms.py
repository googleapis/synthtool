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
import sys
from os.path import normpath
from pathlib import Path
import tempfile

import pytest

from synthtool import transforms
from synthtool import _tracked_paths


@pytest.fixture()
def expand_path_fixtures(tmpdir):
    files = {
        "a.txt": "alpha text",
        "b.py": "beta python",
        "c.md": "see markdown",
        "dira/e.txt": "epsilon text",
        "dira/f.py": "eff python",
        "dirb/suba/g.py": "gamma python",
    }

    for file_name, content in files.items():
        path = tmpdir.join(normpath(file_name))
        path.write_text(content, encoding="utf-8", ensure=True)

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
        ("**/*.py", ["b.py", normpath("dira/f.py"), normpath("dirb/suba/g.py")]),
        (
            "**/*",
            [
                "a.txt",
                "b.py",
                "c.md",
                "dira",
                normpath("dira/e.txt"),
                normpath("dira/f.py"),
                "dirb",
                normpath("dirb/suba"),
                normpath("dirb/suba/g.py"),
            ],
        ),
    ],
)
def test__expand_paths(expand_path_fixtures, input, expected):
    paths = sorted([str(x) for x in transforms._expand_paths(input)])
    assert paths == expected


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        ("e.txt", [normpath("dira/e.txt")]),
        ("*", [normpath("dira/e.txt"), normpath("dira/f.py")]),
    ],
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
        normpath("dira/e.txt"),
        normpath("dira/f.py"),
        normpath("dirb/suba/g.py"),
    ]


def test__file_copy_mode(executable_fixtures):
    executable = "exec.sh"
    destination = executable_fixtures / "exec_copy.sh"

    transforms.move([executable], destination)

    # Check if destination file has execute permission for USER
    if sys.platform != "win32":
        assert destination.stat().mode & stat.S_IXUSR


def test__move_to_dest(expand_path_fixtures):
    tmp_path = Path(str(expand_path_fixtures))
    _tracked_paths.add(expand_path_fixtures)
    dest = Path(str(expand_path_fixtures / "dest"))

    transforms.move(tmp_path, dest, excludes=[normpath("dira/f.py")])

    files = sorted([str(x) for x in transforms._expand_paths("**/*", root="dest")])

    # Assert destination does not contain dira/f.py (excluded)
    assert files == [
        normpath(path)
        for path in [
            "dest/a.txt",
            "dest/b.py",
            "dest/c.md",
            "dest/dira",
            "dest/dira/e.txt",
            "dest/dirb",
            "dest/dirb/suba",
            "dest/dirb/suba/g.py",
        ]
    ]


def test__move_to_dest_subdir(expand_path_fixtures):
    tmp_path = Path(str(expand_path_fixtures))
    _tracked_paths.add(expand_path_fixtures)
    dest = Path(str(expand_path_fixtures / normpath("dest/dira")))

    # Move to a different dir to make sure that move doesn't depend on the cwd
    os.chdir(tempfile.gettempdir())
    transforms.move(tmp_path / "dira", dest, excludes=["f.py"])

    os.chdir(str(tmp_path))
    files = sorted([str(x) for x in transforms._expand_paths("**/*", root="dest")])

    # Assert destination does not contain dira/f.py (excluded)
    assert files == [normpath("dest/dira"), normpath("dest/dira/e.txt")]


def test_simple_replace(expand_path_fixtures):
    count_replaced = transforms.replace(["a.txt", "b.py"], "b..a", "GA")
    assert 1 == count_replaced
    assert "alpha text" == open("a.txt", "rt").read()
    assert "GA python" == open("b.py", "rt").read()


def test_multi_replace(expand_path_fixtures):
    count_replaced = transforms.replace(["a.txt", "b.py"], r"(\w+)a", r"\1z")
    assert 2 == count_replaced
    assert "alphz text" == open("a.txt", "rt").read()
    assert "betz python" == open("b.py", "rt").read()


def test_replace_not_found(expand_path_fixtures):
    count_replaced = transforms.replace(["a.txt", "b.py"], r"z", r"q")
    assert 0 == count_replaced
    assert "alpha text" == open("a.txt", "rt").read()
    assert "beta python" == open("b.py", "rt").read()
