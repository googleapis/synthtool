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

import stat
from pathlib import Path


from synthtool.sources import templates


FIXTURES = Path(__file__).parent / "fixtures"


def test_render():
    t = templates.Templates(FIXTURES)
    result = t.render("example.j2", name="world")

    assert result.name == "example"
    assert result.read_text() == "Hello, world!\n"


def test_render_group():
    t = templates.TemplateGroup(FIXTURES / "group")
    result = t.render(var_a="hello", var_b="world")

    assert (result / "1.txt").read_text() == "hello\n"
    assert (result / "subdir" / "2.txt").read_text() == "world\n"


def test_render_preserve_mode():
    """
    Test that rendering templates correctly preserve file modes.
    """
    source_file = FIXTURES / "executable.j2"
    source_mode = source_file.stat().st_mode

    # Verify source fixture has execute permission for USER
    assert source_mode & stat.S_IXUSR

    t = templates.Templates(FIXTURES)
    result = t.render("executable.j2", name="executable")

    assert result.stat().st_mode == source_mode
