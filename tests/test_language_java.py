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
import shutil
import tempfile
from pathlib import Path
from synthtool.languages import java
import requests_mock

FIXTURES = Path(__file__).parent / "fixtures"

SAMPLE_METADATA = """
<metadata>
  <groupId>com.google.cloud</groupId>
  <artifactId>libraries-bom</artifactId>
  <versioning>
    <latest>3.3.0</latest>
    <release>3.3.0</release>
    <versions>
      <version>1.0.0</version>
      <version>1.1.0</version>
      <version>1.1.1</version>
      <version>1.2.0</version>
      <version>2.0.0</version>
      <version>2.1.0</version>
      <version>2.2.0</version>
      <version>2.2.1</version>
      <version>2.3.0</version>
      <version>2.4.0</version>
      <version>2.5.0</version>
      <version>2.6.0</version>
      <version>2.7.0</version>
      <version>2.7.1</version>
      <version>2.8.0</version>
      <version>2.9.0</version>
      <version>3.0.0</version>
      <version>3.1.0</version>
      <version>3.1.1</version>
      <version>3.2.0</version>
      <version>3.3.0</version>
    </versions>
    <lastUpdated>20191218182827</lastUpdated>
  </versioning>
</metadata>
"""


def test_version_from_maven_metadata():
    assert "3.3.0" == java.version_from_maven_metadata(SAMPLE_METADATA)


def test_latest_maven_version():
    with requests_mock.Mocker() as m:
        m.get(
            "https://repo1.maven.org/maven2/com/google/cloud/libraries-bom/maven-metadata.xml",
            text=SAMPLE_METADATA,
        )
        assert "3.3.0" == java.latest_maven_version(
            group_id="com.google.cloud", artifact_id="libraries-bom"
        )


def test_working_common_templates():
    with tempfile.TemporaryDirectory() as tempdir:
        workdir = shutil.copytree(
            FIXTURES / "java_templates" / "standard", Path(tempdir) / "standard"
        )
        cwd = os.getcwd()
        os.chdir(workdir)

        # generate the common templates
        java.common_templates()
        assert os.path.isfile("README.md")

        os.chdir(cwd)
