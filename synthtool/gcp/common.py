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

from synthtool.languages import node
from synthtool.sources import templates
from synthtool import _tracked_paths

_TEMPLATES_DIR = Path(__file__).parent / "templates"


class CommonTemplates:
    def __init__(self):
        self._templates = templates.Templates(_TEMPLATES_DIR)

    def py_library(self) -> Path:
        raise NotImplemented()

    def node_library(self, **kwargs) -> Path:
        kwargs["metadata"] = node.read_metadata()
        t = templates.TemplateGroup(_TEMPLATES_DIR / "node_library")
        result = t.render(**kwargs)
        _tracked_paths.add(result)
        return result

    def php_library(self, **kwargs) -> Path:
        t = templates.TemplateGroup(_TEMPLATES_DIR / "php_library")
        result = t.render(**kwargs)
        _tracked_paths.add(result)
        return result

    def render(self, template_name: str, **kwargs) -> Path:
        return self._templates.render(template_name, **kwargs)
