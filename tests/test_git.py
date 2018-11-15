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

from unittest import mock

import pytest

from synthtool.sources import git


def test_make_repo_clone_url(monkeypatch):
    monkeypatch.setattr(git, "USE_SSH", True)
    assert (
        git.make_repo_clone_url("theacodes/nox") == "git@github.com:theacodes/nox.git"
    )


def test_make_repo_clone_url_https(monkeypatch):
    monkeypatch.setattr(git, "USE_SSH", False)
    assert (
        git.make_repo_clone_url("theacodes/nox")
        == "https://github.com/theacodes/nox.git"
    )


@pytest.mark.parametrize(
    ("input, expected"),
    [
        ("git@github.com:theacodes/nox.git", {"owner": "theacodes", "name": "nox"}),
        ("https://github.com/theacodes/nox.git", {"owner": "theacodes", "name": "nox"}),
        ("theacodes/nox", {"owner": "theacodes", "name": "nox"}),
        ("theacodes/nox.git", {"owner": "theacodes", "name": "nox"}),
    ],
)
def test_parse_repo_url(input, expected):
    assert git.parse_repo_url(input) == expected


@mock.patch("subprocess.check_output", autospec=True)
def test_get_latest_commit(check_call):
    check_call.return_value = b"abc123\ncommit\nmessage."

    sha, message = git.get_latest_commit()

    assert sha == "abc123"
    assert message == "commit\nmessage."


def test_extract_commmit_message_metadata():
    message = """\
Hello, world!

One: Hello!
Two: 1234
"""
    metadata = git.extract_commmit_message_metadata(message)

    assert metadata == {"One": "Hello!", "Two": "1234"}
