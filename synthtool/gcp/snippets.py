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

import glob
import re
from typing import Dict, List

SNIPPET_REGEX = r"\[START ([a-z0-9_]+)\](.*)\n[\s(\/\/)#(<!--)]+\[END \1\]"


def all_snippets_from_file(sample_file: str) -> Dict[str, str]:
    snippets = {}
    with open(sample_file) as f:
        contents = f.read()
        for match in re.findall(SNIPPET_REGEX, contents, re.DOTALL):
            snippets[match[0]] = match[1]

    return snippets


def all_snippets(snippet_globs: List[str]) -> Dict[str, str]:
    """Walks the samples directory and returns a dictionary of snippet name -> code:

    {
        "snippet_name": "sample code goes here"
    }
    """
    snippets = {}
    for snippet_glob in snippet_globs:
        for file in glob.glob(snippet_glob, recursive=True):
            for snippet, code in all_snippets_from_file(file).items():
                snippets[snippet] = code
    return snippets
