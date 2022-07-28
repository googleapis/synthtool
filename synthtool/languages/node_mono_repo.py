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
from jinja2 import FileSystemLoader, Environment
from pathlib import Path
import re
from synthtool import _tracked_paths, gcp, shell, transforms
from synthtool.gcp import samples, snippets
from synthtool.log import logger
from synthtool.sources import git
from typing import Any, Dict, List, Optional, Callable
import logging
import shutil
from synthtool.languages import common
from datetime import date


_REQUIRED_FIELDS = ["name", "repository", "engines"]
_TOOLS_DIRECTORY = "/synthtool"
_GENERATED_SAMPLES_DIRECTORY = "./samples/generated"


def read_metadata(relative_dir: str):
    """
    read package name and repository in package.json from a Node library.

    Returns:
        data - package.json file as a dict.
    """
    with open(Path(relative_dir, "./package.json").resolve()) as f:
        data = json.load(f)

        if not all(key in data for key in _REQUIRED_FIELDS):
            raise RuntimeError(
                f"package.json is missing required fields {_REQUIRED_FIELDS}"
            )

        repo = git.parse_repo_url(data["repository"])

        data["repository"] = f'{repo["owner"]}/{repo["name"]}'
        data["repository_name"] = repo["name"]
        data["lib_install_cmd"] = f'npm install {data["name"]}'
        engines_field = re.search(r"([0-9][0-9])", data["engines"]["node"])
        assert engines_field is not None
        data["engine"] = engines_field.group()

        return data


def template_metadata(relative_dir: str) -> Dict[str, Any]:
    """Load node specific template metadata.

    Returns:
        Dictionary of metadata. Includes the entire parsed contents of the package.json file if
        present. Other expected fields:
        * quickstart (str): Contents of the quickstart snippet if available, otherwise, ""
        * samples (List[Dict[str, str]]): List of available samples. See synthtool.gcp.samples.all_samples()
    """
    metadata = {}
    try:
        metadata = read_metadata(relative_dir)
    except FileNotFoundError:
        pass

    all_samples = samples.all_samples([str(Path(relative_dir, "samples/*.js"))])

    # quickstart.js sample is special - only include it in the samples list if there is
    # a quickstart snippet present in the file
    quickstart_snippets = list(
        snippets.all_snippets_from_file(
            str(Path(relative_dir, "samples/quickstart.js").resolve())
        ).values()
    )
    metadata["quickstart"] = quickstart_snippets[0] if quickstart_snippets else ""
    metadata["samples"] = list(
        filter(
            lambda sample: sample["file"] != "samples/quickstart.js"
            or metadata["quickstart"],
            all_samples,
        )
    )
    metadata["year"] = date.today().year
    return metadata


def extract_clients(filePath: Path) -> List[str]:
    """
    parse the client name from index.ts file

    Args:
        filePath: the path of index.ts.
    Returns:
        Array of client name string extract from index.ts file.
    """
    with open(filePath, "r") as fh:
        content = fh.read()
    return re.findall(r"\{(.*Client)\}", content)


def generate_index_ts(
    versions: List[str], default_version: str, relative_dir: str, year: str
) -> None:
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
        err_msg = (
            "List of version can't be empty, it must contain default version at least."
        )
        logger.error(err_msg)
        raise AttributeError(err_msg)
    if default_version not in versions:
        err_msg = f"Version {versions} must contain default version {default_version}."
        logger.error(err_msg)
        raise AttributeError(err_msg)

    # To make sure the output is always deterministic.
    versions = sorted(versions)

    # compose default version's index.ts file path
    versioned_index_ts_path = (
        Path(relative_dir) / Path("src") / default_version / "index.ts"
    )
    clients = extract_clients(versioned_index_ts_path)
    if not clients:
        err_msg = f"No client is exported in the default version's({default_version}) index.ts ."
        logger.error(err_msg)
        raise AttributeError(err_msg)

    # compose template directory
    template_path = (
        Path(__file__).parent.parent / "gcp" / "templates" / "node_split_library"
    )
    template_loader = FileSystemLoader(searchpath=str(template_path))
    template_env = Environment(loader=template_loader, keep_trailing_newline=True)
    TEMPLATE_FILE = "index.ts.j2"
    index_template = template_env.get_template(TEMPLATE_FILE)
    # render index.ts content
    output_text = index_template.render(
        versions=versions, default_version=default_version, clients=clients, year=year
    )
    with open(Path(relative_dir, "src/index.ts").resolve(), "w") as fh:
        fh.write(output_text)
    logger.info("successfully generate `src/index.ts`")


def install(hide_output=False):
    """
    Installs all dependencies for the current Node.js library.
    """
    logger.debug("Installing dependencies...")
    shell.run(["npm", "install"], hide_output=hide_output)


def fix(hide_output=False):
    """
    Fixes the formatting in the current Node.js library.
    Before running fix script, run prelint to install extra dependencies
    for samples, but do not fail if it does not succeed.
    """
    logger.debug("Running prelint...")
    shell.run(["npm", "run", "prelint"], check=False, hide_output=hide_output)
    logger.debug("Running fix...")
    shell.run(["npm", "run", "fix"], hide_output=hide_output)


def fix_hermetic(relative_dir, hide_output=False):
    """
    Fixes the formatting in the current Node.js library. It assumes that gts
    is already installed in a well known location on disk:
    """
    logger.debug("Copy eslint config")
    shell.run(
        ["cp", "-r", f"{_TOOLS_DIRECTORY}/node_modules", "."],
        cwd=relative_dir,
        check=True,
        hide_output=hide_output,
    )
    logger.debug("Running fix...")
    shell.run(
        [f"{_TOOLS_DIRECTORY}/node_modules/.bin/gts", "fix"],
        cwd=relative_dir,
        check=False,
        hide_output=hide_output,
    )


def compile_protos(hide_output=False):
    """
    Compiles protos into .json, .js, and .d.ts files using
    compileProtos script from google-gax.
    """
    logger.debug("Compiling protos...")
    shell.run(["npx", "compileProtos", "src"], hide_output=hide_output)


def compile_protos_hermetic(relative_dir, hide_output=False):
    """
    Compiles protos into .json, .js, and .d.ts files using
    compileProtos script from google-gax.
    """
    logger.debug("Compiling protos...")
    shell.run(
        [f"{_TOOLS_DIRECTORY}/node_modules/.bin/compileProtos", "src"],
        cwd=relative_dir,
        check=True,
        hide_output=hide_output,
    )


def postprocess_gapic_library(hide_output=False):
    logger.debug("Post-processing GAPIC library...")
    install(hide_output=hide_output)
    fix(hide_output=hide_output)
    compile_protos(hide_output=hide_output)
    logger.debug("Post-processing completed")


def postprocess_gapic_library_hermetic(relative_dir, hide_output=False):
    logger.debug("Post-processing GAPIC library...")
    fix_hermetic(relative_dir, hide_output=hide_output)
    compile_protos_hermetic(relative_dir, hide_output=hide_output)
    logger.debug("Post-processing completed")


default_staging_excludes = ["README.md", "package.json", "src/index.ts"]
default_templates_excludes: List[str] = []


def _noop(library: Path) -> None:
    pass


def walk_through_owlbot_dirs(dir: Path):
    """
    Walks through all API packages in google-cloud-node/packages

    Returns:
    A list of client libs
    """
    owlbot_dirs = []
    packages_to_exclude = [r"gapic-node-templating"]
    for path_object in dir.glob("packages/**/.OwlBot.yaml"):
        if path_object.is_file() and not re.search(
            "(?:% s)" % "|".join(packages_to_exclude), str(Path(path_object))
        ):
            owlbot_dirs.append(str(Path(path_object).parents[1]))

    return owlbot_dirs


def owlbot_main(
    relative_dir,
    template_path: Optional[Path] = None,
    staging_excludes: Optional[List[str]] = None,
    templates_excludes: Optional[List[str]] = None,
    patch_staging: Callable[[Path], None] = _noop,
) -> None:
    """Copies files from staging and template directories into current working dir.

    Args:
        template_path: path to template directory; omit except in tests.
        staging_excludes: paths to ignore when copying from the staging directory
        templates_excludes: paths to ignore when copying generated templates
        patch_staging: callback function runs on each staging directory before
          copying it into repo root.  Add your regular expression substitution code
          here.

    When there is no owlbot.py file, run this function instead.  Also, when an
    owlbot.py file is necessary, the first statement of owlbot.py should probably
    call this function.

    Depends on owl-bot copying into a staging directory, so your .Owlbot.yaml should
    look a lot like this:

        docker:
            image: gcr.io/repo-automation-bots/owlbot-nodejs:latest

        deep-remove-regex:
            - /owl-bot-staging

        deep-copy-regex:
            - source: /google/cloud/video/transcoder/(.*)/.*-nodejs/(.*)
              dest: /owl-bot-staging/$1/$2

    Also, this function requires a default_version in your .repo-metadata.json.  Ex:
        "default_version": "v1",
    """
    if staging_excludes is None:
        staging_excludes = default_staging_excludes
    if templates_excludes is None:
        templates_excludes = default_templates_excludes

    logging.basicConfig(level=logging.DEBUG)
    # Load the default version defined in .repo-metadata.json.
    default_version = json.load(
        open(Path(relative_dir, ".repo-metadata.json").resolve(), "rt")
    ).get("default_version")
    staging = Path("owl-bot-staging", Path(relative_dir).name).resolve()
    s_copy = transforms.move
    if default_version is None:
        logger.info("No default version found in .repo-metadata.json.  Ok.")
    elif staging.is_dir():
        logger.info(f"Copying files from staging directory ${staging}.")
        # Collect the subdirectories of the staging directory.
        versions = [v.name for v in staging.iterdir() if v.is_dir()]
        # Reorder the versions so the default version always comes last.
        versions = [v for v in versions if v != default_version] + [default_version]
        logger.info(f"Collected versions ${versions} from ${staging}")

        # Copy each version directory into the root.
        for version in versions:
            library = staging / version
            _tracked_paths.add(library)
            patch_staging(library)
            s_copy([library], destination=relative_dir, excludes=staging_excludes)
        # The staging directory should never be merged into the main branch.
        shutil.rmtree(staging)
    else:
        # Collect the subdirectories of the src directory.
        src = Path(Path(relative_dir), "src").resolve()
        versions = [v.name for v in src.iterdir() if v.is_dir()]
        # Reorder the versions so the default version always comes last.
        versions = [v for v in versions if v != default_version] + [default_version]
        logger.info(f"Collected versions ${versions} from ${src}")

    common_templates = gcp.CommonTemplates(template_path)
    common_templates.excludes.extend(templates_excludes)
    if default_version:
        templates = common_templates.node_mono_repo_library(
            relative_dir=relative_dir,
            source_location="build/src",
            versions=versions,
            default_version=default_version,
        )
        s_copy([templates], destination=relative_dir, excludes=templates_excludes)
        postprocess_gapic_library_hermetic(relative_dir=relative_dir)
    else:
        templates = common_templates.node_mono_repo_library(
            relative_dir=relative_dir, source_location="build/src"
        )
        s_copy([templates], destination=relative_dir, excludes=templates_excludes)

    library_version = template_metadata(str(Path(relative_dir))).get("version")
    if library_version:
        common.update_library_version(
            library_version,
            str(Path(relative_dir, _GENERATED_SAMPLES_DIRECTORY).resolve()),
        )


def owlbot_entrypoint(
    template_path: Optional[Path] = None,
    staging_excludes: Optional[List[str]] = None,
    templates_excludes: Optional[List[str]] = None,
    patch_staging: Callable[[Path], None] = _noop,
):
    owlbot_dirs = walk_through_owlbot_dirs(Path.cwd())
    for dir in owlbot_dirs:
        owlbot_main(
            dir, template_path, staging_excludes, templates_excludes, patch_staging
        )


if __name__ == "__main__":
    owlbot_entrypoint()
