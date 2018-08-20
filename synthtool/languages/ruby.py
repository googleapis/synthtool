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

from pathlib import Path
import re
from typing import Iterable, Union

import synthtool

PathOrStr = Union[str, Path]
ListOfPathsOrStrs = Iterable[PathOrStr]


def merge_gemspec(src: str, dest: str, path: Path):
    """Merge function for ruby gemspecs.

    Preserves the gem version and homepage fields from the destination, and
    copies the remaining fields from the newly generated source.

    Args:
        src: Source gemspec content from gapic
        dest: Destination gemspec content
        path: Destination gemspec path

    Returns:
        The merged gemspec content.
    """
    regex = re.compile(r'^\s+gem.version\s*=\s*"[\d\.]+"$', flags=re.MULTILINE)
    match = regex.search(dest)
    if match:
        src = regex.sub(match.group(0), src, count=1)

    regex = re.compile(r'^\s+gem.homepage\s*=\s*"[^"]+"$', flags=re.MULTILINE)
    match = regex.search(dest)
    if match:
        src = regex.sub(match.group(0), src, count=1)

    return src


def delete_method(sources: ListOfPathsOrStrs, method_name: str):
    """Deletes a Ruby method, including the leading comment if any.

    Args:
        sources: Source file or list of files
        method_name: Name of the method to delete
    """
    regex = f"\\n\\n(\\s+#[^\\n]*\\n)*\\n*(\\s+)def\\s+{method_name}[^\\n]+\\n+(\\2\\s\\s[^\\n]+\\n+)*\\2end\\n"
    synthtool.replace(sources, regex, "\n")
