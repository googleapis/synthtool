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
from typing import Dict, List, Optional

from synthtool import _tracked_paths
from synthtool.languages import node
from synthtool.log import logger
from synthtool.sources import git, templates


TEMPLATES_URL: str = git.make_repo_clone_url("googleapis/synthtool")
DEFAULT_TEMPLATES_PATH = "synthtool/gcp/templates"
LOCAL_TEMPLATES: Optional[str] = os.environ.get("SYNTHTOOL_TEMPLATES")


class CommonTemplates:
    def __init__(self, template_path: Optional[Path] = None):
        if template_path:
            self._template_root = template_path
        elif LOCAL_TEMPLATES:
            logger.debug(f"Using local templates at {LOCAL_TEMPLATES}")
            self._template_root = Path(LOCAL_TEMPLATES)
        else:
            templates_git = git.clone(TEMPLATES_URL)
            self._template_root = templates_git / DEFAULT_TEMPLATES_PATH

        self._templates = templates.Templates(self._template_root)
        self.excludes = []  # type: List[str]

    def _generic_library(self, directory: str, **kwargs) -> Path:
        # load common repo meta information (metadata that's not language specific).
        if "metadata" in kwargs:
            self._load_generic_metadata(kwargs["metadata"])
            # if no samples were found, don't attempt to render a
            # samples/README.md.
            if "samples" not in kwargs["metadata"] or not kwargs["metadata"]["samples"]:
                self.excludes.append("samples/README.md")

        t = templates.TemplateGroup(self._template_root / directory, self.excludes)
        result = t.render(**kwargs)
        _tracked_paths.add(result)

        return result

    def py_samples(self, **kwargs) -> Path:
        # kwargs["metadata"] is required to load values from .repo-metadata.json
        if "metadata" not in kwargs:
            kwargs["metadata"] = {}
        return self._generic_library("python_samples", **kwargs)

    def py_library(self, **kwargs) -> Path:
        # kwargs["metadata"] is required to load values from .repo-metadata.json
        if "metadata" not in kwargs:
            kwargs["metadata"] = {}
        # rename variable to accomodate existing synth.py files
        if "system_test_dependencies" in kwargs:
            kwargs["system_test_local_dependencies"] = kwargs[
                "system_test_dependencies"
            ]
            logger.warning(
                "Template argument 'system_test_dependencies' is deprecated."
                "Use 'system_test_local_dependencies' or 'system_test_external_dependencies'"
                "instead."
            )

        # Set default Python versions for noxfile.py
        if "default_python_version" not in kwargs:
            kwargs["default_python_version"] = "3.8"
        if "unit_test_python_versions" not in kwargs:
            kwargs["unit_test_python_versions"] = ["3.6", "3.7", "3.8"]
            if "microgenerator" not in kwargs:
                kwargs["unit_test_python_versions"] = ["2.7", "3.5"] + kwargs[
                    "unit_test_python_versions"
                ]

        if "system_test_python_versions" not in kwargs:
            kwargs["system_test_python_versions"] = ["3.8"]
            if "microgenerator" not in kwargs:
                kwargs["system_test_python_versions"] = ["2.7"] + kwargs[
                    "system_test_python_versions"
                ]

        # Don't add samples templates if there are no samples
        if "samples" not in kwargs:
            self.excludes += ["samples/AUTHORING_GUIDE.md", "samples/CONTRIBUTING.md"]

        return self._generic_library("python_library", **kwargs)

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

        kwargs["metadata"] = node.template_metadata()
        kwargs["publish_token"] = node.get_publish_token(kwargs["metadata"]["name"])

        # generate root-level `src/index.ts` to export multiple versions and its default clients
        if "versions" in kwargs and "default_version" in kwargs:
            node.generate_index_ts(
                versions=kwargs["versions"], default_version=kwargs["default_version"]
            )

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
        self._load_partials(metadata)

        # Loads repo metadata information from the default location if it
        # hasn't already been set. Some callers may have already loaded repo
        # metadata, so we don't need to do it again or overwrite it. Also, only
        # set the "repo" key.
        if "repo" not in metadata:
            metadata["repo"] = _load_repo_metadata()

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
