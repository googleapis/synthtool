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
from pathlib import Path
from typing import Any, Dict
from synthtool.sources import git
from synthtool.gcp import samples, snippets
from synthtool import log, shell

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


def is_gapic_library():
    """
    Checks if the library is a GAPIC library that needs a special
    post-processing of its proto files.  A library that depends on
    `google-gax` and has at least one file matching
    `src/**/*_proto_list.json` (an input for `compileProtos` script)
    is considered a GAPIC library.

    Returns:
        True if a library is GAPIC and compileProtos call is needed.
    """
    with open("package.json", "r") as package_json:
        package_json_obj = json.load(package_json)
    if "dependencies" not in package_json_obj:
        log.debug("No dependencies in package.json; not a GAPIC library.")
        return False
    if "google-gax" not in package_json_obj["dependencies"]:
        log.debug("Does not depend on google-gax, not a GAPIC library.")
        return False
    for path in Path("src").rglob("*_proto_list.json"):
        log.debug(f"Found {path}, it's a GAPIC library.")
        return True
    log.debug("No src/**/*_proto_list.json found; not a GAPIC library.")
    return False


def postprocess(install=True, prelint=True, fix=True, protos=True, hide_output=False):
    """
    Runs common post-processing for Node library.
    """
    log.debug("Node.js library post-processing started.")
    if install:
        log.debug("Installing dependencies...")
        shell.run(["npm", "install"], hide_output=hide_output)
    else:
        log.debug("Skipping dependency installation.")
    if prelint:
        log.debug("Running prelint...")
        shell.run(["npm", "run", "prelint"], hide_output=hide_output)
    else:
        log.debug("Skipping prelint.")
    if fix:
        log.debug("Running fix...")
        shell.run(["npm", "run", "fix"], hide_output=hide_output)
    else:
        log.debug("Skipping fix.")
    # If we have protos to compile, do it now
    if protos and is_gapic_library():
        log.debug("Compiling protos...")
        shell.run(["npx", "compileProtos", "src"], hide_output=hide_output)
    else:
        log.debug("Skipping protos compilation.")
    log.debug("Node.js library post-processing finished.")
