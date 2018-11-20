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
from synthtool import cache
from synthtool import log
from synthtool import shell
from pathlib import Path


def format_code(path: str, version: str = "1.6") -> None:
    """
    Runs the google-java-format jar against all .java files found within the
    provided path.
    """
    jar_name = f"google-java-format-{version}.jar"
    jar = cache.get_cache_dir() / jar_name
    if not jar.exists():
        _download_formatter(version, jar)

    # Find all .java files in path and run the formatter on them
    log.info("Looking for java files in {}".format(os.path.join(path, "**/*.java")))
    files = list(glob.iglob(os.path.join(path, "**/*.java"), recursive=True))

    # Run the formatter as a jar file
    log.info("Running java formatter on {} files".format(len(files)))
    shell.run(["java", "-jar", jar, "--replace"] + files)


def _download_formatter(version: str, dest: Path) -> None:
    url = f"https://github.com/google/google-java-format/releases/download/google-java-format-{version}/google-java-format-{version}-all-deps.jar"
    log.info("Downloading java formatter")
    shell.run(["curl", "-L", "-o", dest, url], hide_output=False)
