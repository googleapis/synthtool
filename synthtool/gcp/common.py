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
from typing import List

from synthtool.languages import node
from synthtool.sources import templates
from synthtool.gcp.templates.metadata import (
    Metadata,
    JavaMetadata,
    NodejsMetadata,
)
from synthtool import __main__
from synthtool import _tracked_paths
from synthtool import metadata

_TEMPLATES_DIR = Path(__file__).parent / "templates"
_RE_SAMPLE_COMMENT_START = r"\[START \w+_quickstart\w*]"
_RE_SAMPLE_COMMENT_END = r"\[END \w+_quickstart\w*]"


class CommonTemplates:
    def __init__(self):
        self._templates = templates.Templates(_TEMPLATES_DIR)
        self.excludes = []  # type: List[str]

    def _generic_library(self, directory: str, **kwargs) -> Path:
        # load common repo meta information (metadata that's not language specific).

        if "metadata" in kwargs:
            # if no samples were found, don't attempt to render a
            # samples/README.md.
            if not kwargs["metadata"]["samples"]:
                self.excludes.append("samples/README.md")

        t = templates.TemplateGroup(_TEMPLATES_DIR / directory, self.excludes)
        result = t.render(**kwargs)
        _tracked_paths.add(result)
        metadata.add_template_source(
            name=directory, origin="synthtool.gcp", version=__main__.VERSION
        )
        return result

    def py_library(self, **kwargs) -> Path:
        kwargs["metadata"] = Metadata(kwargs.get("metadata"))
        return self._generic_library("python_library", **kwargs)

    def java_library(self, **kwargs) -> Path:
        kwargs["metadata"] = JavaMetadata(kwargs.get("metadata"))
        return self._generic_library("java_library", **kwargs)

    def node_library(self, **kwargs) -> Path:
        kwargs["metadata"] = NodejsMetadata(node.read_metadata())
        kwargs["publish_token"] = node.get_publish_token(kwargs["metadata"]["name"])
        return self._generic_library("node_library", **kwargs)

    def php_library(self, **kwargs) -> Path:
        return self._generic_library("php_library", **kwargs)

    def ruby_library(self, **kwargs) -> Path:
        kwargs["metadata"] = Metadata(kwargs.get("metadata"))
        return self._generic_library("ruby_library", **kwargs)

    def render(self, template_name: str, **kwargs) -> Path:
        return self._templates.render(template_name, **kwargs)
