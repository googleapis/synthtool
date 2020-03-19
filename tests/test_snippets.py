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
from synthtool.gcp import snippets

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_snippets():
    cwd = os.getcwd()
    os.chdir(FIXTURES)

    all_snippets = snippets.all_snippets(["snippets/*.java", "snippets/*.xml"])
    assert len(all_snippets) == 2

    assert (
        all_snippets["monitoring_quickstart"]
        == """
public class MonitoringQuickstartSample {
    // do something
}

"""
    )
    assert (
        all_snippets["monitoring_install_with_bom"]
        == """<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>com.google.cloud</groupId>
      <artifactId>libraries-bom</artifactId>
      <version>3.5.0</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>

<dependencies>
  <dependency>
    <groupId>com.google.cloud</groupId>
    <artifactId>google-cloud-monitoring</artifactId>
  </dependency>
</dependencies>
"""
    )

    os.chdir(cwd)


def test_interleaving_snippets():
    cwd = os.getcwd()
    os.chdir(FIXTURES)

    all_snippets = snippets.all_snippets_from_file("snippets/interleaved.js")
    assert len(all_snippets) == 2

    assert (
        all_snippets["interleave_snippet_1"]
        == """var line1 = 1;
var line2 = 2;
"""
    )

    assert (
        all_snippets["interleave_snippet_2"]
        == """var line2 = 2;
var line3 = 3;
"""
    )

    os.chdir(cwd)


def test_nested_snippets():
    cwd = os.getcwd()
    os.chdir(FIXTURES)

    all_snippets = snippets.all_snippets_from_file("snippets/nested.js")
    assert len(all_snippets) == 2

    assert (
        all_snippets["nested_snippet_1"]
        == """var line1 = 1;
var line2 = 2;
var line3 = 3;
"""
    )

    assert (
        all_snippets["nested_snippet_2"]
        == """var line2 = 2;
"""
    )

    os.chdir(cwd)


def test_non_existent_file():
    cwd = os.getcwd()
    os.chdir(FIXTURES)

    all_snippets = snippets.all_snippets_from_file("snippets/non-existent-file.foo")
    assert len(all_snippets) == 0

    os.chdir(cwd)
