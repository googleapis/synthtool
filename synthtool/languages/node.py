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
from typing import Any, Dict, List
from synthtool.sources import git
from synthtool.gcp import samples, snippets
import pathlib
from jinja2 import Template, FileSystemLoader, Environment
import re
from synthtool import log
import os
from pathlib import Path

_REQUIRED_FIELDS = ["name", "repository"]


def read_metadata():
    """
    read package name and repository in package.json from a Node library.

    Returns:
        data - package.json file as a dict.
    """
    with open("./package.json") as f:
        data = json.load(f)

        if not all(key in data for key in _REQUIRED_FIELDS):
            raise RuntimeError(
                f"package.json is missing required fields {_REQUIRED_FIELDS}"
            )

        repo = git.parse_repo_url(data["repository"])

        data["repository"] = f'{repo["owner"]}/{repo["name"]}'
        data["repository_name"] = repo["name"]
        data["lib_install_cmd"] = f'npm install {data["name"]}'

        return data


def template_metadata() -> Dict[str, Any]:
    """Load node specific template metadata.

    Returns:
        Dictionary of metadata. Includes the entire parsed contents of the package.json file if
        present. Other expected fields:
        * quickstart (str): Contents of the quickstart snippet if available, otherwise, ""
        * samples (List[Dict[str, str]]): List of available samples. See synthtool.gcp.samples.all_samples()
    """
    metadata = {}
    try:
        metadata = read_metadata()
    except FileNotFoundError:
        pass

    all_samples = samples.all_samples(["samples/*.js"])

    # quickstart.js sample is special - only include it in the samples list if there is
    # a quickstart snippet present in the file
    quickstart_snippets = list(
        snippets.all_snippets_from_file("samples/quickstart.js").values()
    )
    metadata["quickstart"] = quickstart_snippets[0] if quickstart_snippets else ""
    metadata["samples"] = list(
        filter(
            lambda sample: sample["file"] != "samples/quickstart.js"
            or metadata["quickstart"],
            all_samples,
        )
    )
    return metadata


def get_publish_token(package_name: str):
    """
    parses the package_name into the name of the token to publish the package.

    Example:
        @google-cloud/storage => google-cloud-storage-npm-token
        dialogflow => dialogflow-npm-token

    Args:
        package: Name of the npm package.
    Returns:
        The name of the key to fetch the publish token.
    """
    return package_name.strip("@").replace("/", "-") + "-npm-token"


def extract_clients(filePath: str) -> List[str]:
    """
    parse the client name from index.ts file

    Args:
        filePath: the path of index.ts.
    Returns:
        Array of client name string extract from index.ts file.
    """
    content = ""

    try:
        with open(filePath, "r") as fh:
            content = fh.read()
    except FileNotFoundError:
        err_msg = f"Failed to find {filePath}."
        log.error(err_msg)
        raise FileNotFoundError(err_msg)
    return re.findall(r"\{(.*Client)\}", content)


def generate_index_ts(versions: List[str], default_version: str) -> bool:
    """
    generate src/index.ts to export the client name and versions in the client library.

    Args:
      versions: the list of versions, like: ['v1', 'v1beta1', ...]
      default_version: a stable version provided by API producer. It must exist in argument versions.
    Return:
      True/False: return true if successfully generate src/index.ts, vice versa.
    """
    # sanitizer the input arguments
    if len(versions) < 1:
        err_msg = "List of version can't be empty, it must contain default version at least."
        log.error(err_msg)
        raise AttributeError(err_msg)
    if default_version not in versions:
        err_msg = f"Version {versions} must contain default version {default_version}."
        log.error(err_msg)
        raise AttributeError(err_msg)

    # compose default version's index.ts file path
    versioned_index_ts_path = pathlib.Path("src") / default_version / "index.ts"
    clients = extract_clients(versioned_index_ts_path)
    if len(clients) == 0:
        err_msg = f"No client is exported in the default version's({default_version}) index.ts ."
        log.error(err_msg)
        return False

    # compose template directory
    templatePath = (
        Path(__file__).parent.parent / "gcp" / "templates" / "node_split_library"
    )
    templateLoader = FileSystemLoader(searchpath=templatePath)
    templateEnv = Environment(loader=templateLoader, keep_trailing_newline=True)
    TEMPLATE_FILE = "index.ts.j2"
    index_template = templateEnv.get_template(TEMPLATE_FILE)
    # render index.ts content
    outputText = index_template.render(
        versions=versions, default_version=default_version, clients=clients
    )
    with open("src/index.ts", "w") as fh:
        fh.write(outputText)
    return True
