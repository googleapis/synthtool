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

import json
import os
from pathlib import Path

from synthtool.languages import node
from synthtool.sources import templates
from synthtool import __main__
from synthtool import _tracked_paths
from synthtool import metadata


_TEMPLATES_DIR = Path(__file__).parent / "templates"


class CommonTemplates:
    def __init__(self):
        self._templates = templates.Templates(_TEMPLATES_DIR)

    def _generic_library(self, directory: str, **kwargs) -> Path:
        self._load_generic_metadata(kwargs["metadata"])
        t = templates.TemplateGroup(_TEMPLATES_DIR / directory)
        result = t.render(**kwargs)
        _tracked_paths.add(result)
        metadata.add_template_source(
            name=directory, origin="synthtool.gcp", version=__main__.VERSION
        )
        return result

    def py_library(self, **kwargs) -> Path:
        return self._generic_library("python_library", **kwargs)

    def node_library(self, **kwargs) -> Path:
        kwargs["metadata"] = node.read_metadata()
        kwargs["publish_token"] = node.get_publish_token(kwargs["metadata"]["name"])
        return self._generic_library("node_library", **kwargs)

    def php_library(self, **kwargs) -> Path:
        return self._generic_library("php_library", **kwargs)

    def render(self, template_name: str, **kwargs) -> Path:
        return self._templates.render(template_name, **kwargs)

    #
    # loads additional meta information from:
    #
    # .cloud-repo-tools.json: which contains information that helps generate
    #  README files with samples.
    #
    # .repo-metadata.json: which contains general meta-info about git repo.
    #
    def _load_generic_metadata(self, metadata):
        # TODO: replace with loading from samples folder.
        metadata["samples"] = {}

        if os.path.exists("./.cloud-repo-tools.json"):
            with open("./.cloud-repo-tools.json") as f:
                metadata["samples"] = json.load(f)

        metadata["repo"] = {}

        if os.path.exists("./.repo-metadata.json"):
            with open("./.repo-metadata.json") as f:
                metadata["repo"] = json.load(f)
