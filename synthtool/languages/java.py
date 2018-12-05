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

import glob
import os
import requests
from synthtool import cache
from synthtool import log
from synthtool import shell
from pathlib import Path

JAR_DOWNLOAD_URL = "https://github.com/google/google-java-format/releases/download/google-java-format-{version}/google-java-format-{version}-all-deps.jar"
DEFAULT_FORMAT_VERSION = "1.6"


def format_code(
    path: str, version: str = DEFAULT_FORMAT_VERSION, times: int = 2
) -> None:
    """
    Runs the google-java-format jar against all .java files found within the
    provided path.
    """
    jar_name = f"google-java-format-{version}.jar"
    jar = cache.get_cache_dir() / jar_name
    if not jar.exists():
        _download_formatter(version, jar)

    # Find all .java files in path and run the formatter on them
    files = list(glob.iglob(os.path.join(path, "**/*.java"), recursive=True))

    # Run the formatter as a jar file
    log.info("Running java formatter on {} files".format(len(files)))
    for _ in range(times):
        shell.run(["java", "-jar", str(jar), "--replace"] + files)


def _download_formatter(version: str, dest: Path) -> None:
    log.info("Downloading java formatter")
    url = JAR_DOWNLOAD_URL.format(version=version)
    response = requests.get(url)
    response.raise_for_status()
    with open(dest, "wb") as fh:
        fh.write(response.content)
