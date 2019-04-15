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
import re
import yaml
from pathlib import Path
from typing import List, Dict

from synthtool.languages import node
from synthtool.sources import templates
from synthtool import __main__
from synthtool import _tracked_paths
from synthtool import metadata


_TEMPLATES_DIR = Path(__file__).parent / "templates"
_RE_SAMPLE_COMMENT_START = r"\[START \w+_quickstart]"
_RE_SAMPLE_COMMENT_END = r"\[END \w+_quickstart]"


class CommonTemplates:
    def __init__(self):
        self._templates = templates.Templates(_TEMPLATES_DIR)
        self.excludes = []  # type: List[str]

    def _generic_library(self, directory: str, **kwargs) -> Path:
        # load common repo meta information (metadata that's not language specific).
        if "metadata" in kwargs:
            self._load_generic_metadata(kwargs["metadata"])
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
        return self._generic_library("python_library", **kwargs)

    def node_library(self, **kwargs) -> Path:
        # TODO: once we've migrated all Node.js repos to either having
        #  .repo-metadata.json, or excluding README.md, we can remove this.
        if not os.path.exists("./.repo-metadata.json"):
            self.excludes.append("README.md")
            if "samples/README.md" not in self.excludes:
                self.excludes.append("samples/README.md")

        kwargs["metadata"] = node.read_metadata()
        kwargs["publish_token"] = node.get_publish_token(kwargs["metadata"]["name"])
        return self._generic_library("node_library", **kwargs)

    def php_library(self, **kwargs) -> Path:
        return self._generic_library("php_library", **kwargs)

    def render(self, template_name: str, **kwargs) -> Path:
        return self._templates.render(template_name, **kwargs)

    def _load_generic_metadata(self, metadata: Dict):
        """
        loads additional meta information from .repo-metadata.json.
        """
        self._load_samples(metadata)
        self._load_partials(metadata)

        metadata["repo"] = {}
        if os.path.exists("./.repo-metadata.json"):
            with open("./.repo-metadata.json") as f:
                metadata["repo"] = json.load(f)

    def _load_samples(self, metadata: Dict):
        """
        walks samples directory and builds up samples data-structure:

        {
            "name": "Requester Pays",
            "file": "requesterPays.js"
        }
        """
        metadata["samples"] = []
        samples_dir = Path(os.getcwd()) / "samples"
        if os.path.exists(samples_dir):
            files = os.listdir(samples_dir)
            files.sort()
            for file in files:
                if re.match(r"\w+\.js$", file):
                    if file == "quickstart.js":
                        metadata["quickstart"] = self._read_quickstart(samples_dir)
                    # only add quickstart file to samples list if code sample is found.
                    if file == "quickstart.js" and not metadata.get("quickstart", None):
                        continue
                    metadata["samples"].append(
                        {"name": decamelize(file[:-3]), "file": file}
                    )

    def _read_quickstart(self, samples_dir: Path) -> str:
        """
        quickstart is a special case, it should be read from disk and displayed
        in README.md rather than pushed into samples array.
        """
        reading = False
        quickstart = ""

        with open(samples_dir / "quickstart.js") as f:
            while True:
                line = f.readline()
                if not line or re.search(_RE_SAMPLE_COMMENT_END, line):
                    break
                if reading:
                    quickstart += line
                if re.search(_RE_SAMPLE_COMMENT_START, line):
                    reading = True

        return quickstart

    def _load_partials(self, metadata: Dict):
        """
        hand-crafted artisinal markdown can be provided in a .readme-partials.yml.
        The following fields are currently supported:

        introduction: a more thorough introduction than metadata["description"].
        body: custom body to include in the usage section of the document.
        """
        cwd_path = Path(os.getcwd())
        partials_file = None
        for file in [".readme-partials.yml", ".readme-partials.yaml"]:
            if os.path.exists(cwd_path / file):
                partials_file = cwd_path / file
                break
        if not partials_file:
            return
        with open(partials_file) as f:
            metadata["partials"] = yaml.load(f, Loader=yaml.SafeLoader)


def decamelize(value: str):
    """ parser to convert fooBar.js to Foo Bar. """
    if not value:
        return ""
    str_decamelize = re.sub("^.", value[0].upper(), value)  # apple -> Apple.
    str_decamelize = re.sub(
        "([A-Z]+)([A-Z])([a-z0-9])", r"\1 \2\3", str_decamelize
    )  # ACLBatman -> ACL Batman.
    return re.sub("([a-z0-9])([A-Z])", r"\1 \2", str_decamelize)  # FooBar -> Foo Bar.
