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
_RE_SAMPLE_COMMENT_START = r"\[START \w+_quickstart\w*]"
_RE_SAMPLE_COMMENT_END = r"\[END \w+_quickstart\w*]"


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
        # kwargs["metadata"] is required to load values from .repo-metadata.json
        if "metadata" not in kwargs:
            kwargs["metadata"] = {}

        templates = "python_split_library"
        # Temporarily allow two sets of python templates
        # Use `python_library` if the library is in google-cloud-python
        # TODO: Remove once google-cloud-python has no libraries in it
        if os.path.exists("./.repo-metadata.json"):
            with open("./.repo-metadata.json") as f:
                metadata = json.load(f)
            if metadata["repo"] == "googleapis/google-cloud-python":
                templates = "python_library"

        return self._generic_library(templates, **kwargs)

    def java_library(self, **kwargs) -> Path:
        # kwargs["metadata"] is required to load values from .repo-metadata.json
        if "metadata" not in kwargs:
            kwargs["metadata"] = {}
        return self._generic_library("java_library", **kwargs)

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

    def ruby_library(self, **kwargs) -> Path:
        # kwargs["metadata"] is required to load values from .repo-metadata.json
        if "metadata" not in kwargs:
            kwargs["metadata"] = {}
        return self._generic_library("ruby_library", **kwargs)

    def render(self, template_name: str, **kwargs) -> Path:
        return self._templates.render(template_name, **kwargs)

    def _load_generic_metadata(self, metadata: Dict):
        """
        loads additional meta information from .repo-metadata.json.
        """
        self._load_samples(metadata)
        self._load_partials(metadata)

        # Loads repo metadata information from the default location if it
        # hasn't already been set. Some callers may have already loaded repo
        # metadata, so we don't need to do it again or overwrite it. Also, only
        # set the "repo" key.
        if "repo" not in metadata:
            metadata["repo"] = _load_repo_metadata()

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
                if re.match(r"[\w.\-]+\.js$", file):
                    if file == "quickstart.js":
                        metadata["quickstart"] = self._read_quickstart(samples_dir)
                    # only add quickstart file to samples list if code sample is found.
                    if file == "quickstart.js" and not metadata.get("quickstart", None):
                        continue
                    sample_metadata = {"title": decamelize(file[:-3]), "file": file}
                    sample_metadata.update(
                        self._read_sample_metadata_comment(samples_dir, file)
                    )
                    metadata["samples"].append(sample_metadata)

    def _read_sample_metadata_comment(self, samples_dir: Path, file: str) -> Dict:
        """
        Additional meta-information can be provided through embedded comments:

        // sample-metadata:
        //   title: ACL (Access Control)
        //   description: Demonstrates setting access control rules.
        //   usage: node iam.js --help
        """
        sample_metadata = {}  # type: Dict[str, str]
        with open(samples_dir / file) as f:
            contents = f.read()
            match = re.search(
                r"(?P<metadata>// *sample-metadata:([^\n]+|\n//)+)", contents, re.DOTALL
            )
            if match:
                # the metadata yaml is stored in a comments, remove the
                # prefix so that we can parse the yaml contained.
                sample_metadata_string = re.sub(
                    r"((#|//) ?)", "", match.group("metadata")
                )
                sample_metadata = yaml.load(
                    sample_metadata_string, Loader=yaml.SafeLoader
                )["sample-metadata"]
        return sample_metadata

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

        body: custom body to include in the usage section of the document.
        samples_body: an optional body to place below the table of contents
          in samples/README.md.
        introduction: a more thorough introduction than metadata["description"].
        title: provide markdown to use as a custom title.
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


def _load_repo_metadata(metadata_file: str = "./.repo-metadata.json") -> Dict:
    """Parse a metadata JSON file into a Dict.

    Currently, the defined fields are:
    * `name` - The service's API name
    * `name_pretty` - The service's API title. This will be used for generating titles on READMEs
    * `product_documentation` - The product documentation on cloud.google.com
    * `client_documentation` - The client library reference documentation
    * `issue_tracker` - The public issue tracker for the product
    * `release_level` - The release level of the client library. One of: alpha, beta, ga, deprecated
    * `language` - The repo language. One of dotnet, go, java, nodejs, php, python, ruby
    * `repo` - The GitHub repo in the format {owner}/{repo}
    * `distribution_name` - The language-idiomatic package/distribution name
    * `api_id` - The API ID associated with the service. Fully qualified identifier use to
      enable a service in the cloud platform (e.g. monitoring.googleapis.com)
    * `requires_billing` - Whether or not the API requires billing to be configured on the
      customer's acocunt

    Args:
        metadata_file (str, optional): Path to the metadata json file

    Returns:
        A dictionary of metadata. This may not necessarily include all the defined fields above.
    """
    if os.path.exists(metadata_file):
        with open(metadata_file) as f:
            return json.load(f)
    return {}
