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
import sys
import subprocess
from synthtool import shell, transforms
from synthtool.gcp import samples, snippets
from synthtool.log import logger
from synthtool.sources import git
from typing import Any, Dict, List, Optional, Callable
import shutil
from synthtool.languages import common
from datetime import date
import logging
from os import system
from synthtool import _tracked_paths
from synthtool import gcp

_REQUIRED_FIELDS = ["name", "repository", "engines"]
_TOOLS_DIRECTORY = "/synthtool"
_GENERATED_SAMPLES_DIRECTORY = "./samples/generated"
PACKAGE_DIRECTORIES = ["packages", "handwritten"]
PACKAGE_DIRECTORIES_REGEX = f"((?:{'|'.join(PACKAGE_DIRECTORIES)})/.*)"


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

        repo_url = (
            data["repository"]
            if isinstance(data["repository"], str)
            else data["repository"]["url"]
        )

        repo = git.parse_repo_url(repo_url)
        data["directory_path"] = (
            data["repository"]
            if isinstance(data["repository"], str)
            else f'{data["repository"]["directory"]}'
        )
        data["full_directory_path"] = (
            data["repository"]
            if isinstance(data["repository"], str)
            else f'{repo["owner"]}/{repo["name"]}/{data["directory_path"]}'
        )
        data["homepage"] = (
            data["repository"]
            if isinstance(data["repository"], str)
            else data["homepage"]
        )
        data["repository"] = f'{repo["owner"]}/{repo["name"]}'
        data["repository_name"] = repo["name"]
        data["lib_install_cmd"] = f'npm install {data["name"]}'
        engines_field = re.search(r"([0-9][0-9])", data["engines"]["node"])
        assert engines_field is not None
        data["engine"] = engines_field.group()

        return data


def copy_list_sample_to_quickstart(relative_dir: str):
    # If there is no samples directory, return early
    if not Path(relative_dir, "samples").resolve().exists():
        return
    # Check if the quickstart exists, so we don't overwrite it.
    if Path(relative_dir, "samples", "quickstart.js").resolve().exists():
        return
    # Look for samples that contain 'list', since we don't need to set up resources for tests
    samples = common.get_sample_metadata_files(
        Path(relative_dir, _GENERATED_SAMPLES_DIRECTORY).resolve(), regex=r"list"
    )
    # If there aren't any list-methods, just pick the first generated sample
    if not samples:
        samples = common.get_sample_metadata_files(
            Path(relative_dir, _GENERATED_SAMPLES_DIRECTORY).resolve(), regex=r".*"
        )
    # Confirm that the file exists (array could be empty)
    if Path(relative_dir, samples[0]).resolve():
        shutil.copyfile(
            Path(relative_dir, samples[0]).resolve(),
            Path(relative_dir, "samples", "quickstart.js").resolve(),
        )
        # Fix the sample tag
        with open(Path(relative_dir, "samples", "quickstart.js").resolve(), "r") as f:
            data = str(f.read())
            data = re.sub(r"_.*]", r"_quickstart]", data, 2)
        with open(Path(relative_dir, "samples", "quickstart.js").resolve(), "w") as f:
            f.write(data)
    # If there are no generated samples, just write to an empty file
    else:
        with open(Path(relative_dir, "samples", "quickstart.js").resolve(), "w+") as f:
            f.write("No sample available")


def write_release_please_config(owlbot_dirs):
    ignore_file = Path("ignore.json")
    ignore_list = []
    if ignore_file.is_file():
        with open(ignore_file, "r") as f:
            try:
                ignore_list = json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Could not decode {ignore_file}, ignoring.")

    config_path = Path("release-please-config.json")
    submodules_path = Path("release-please-submodules.json")

    with open(config_path, "r") as f:
        config_data = json.load(f)

    submodules_data = None
    if submodules_path.is_file():
        with open(submodules_path, "r") as f:
            submodules_data = json.load(f)

    # If submodules config exists, use it as an exclusion list from bundled release
    non_bundled_packages = (
        set(submodules_data.get("packages", {}).keys()) if submodules_data else set()
    )

    for dir in owlbot_dirs:
        result = re.search(PACKAGE_DIRECTORIES_REGEX, dir)
        assert result is not None
        package_name = result.group()

        if package_name in ignore_list:
            continue

        if package_name in non_bundled_packages:
            # remove from bundled release
            if package_name in config_data["packages"]:
                del config_data["packages"][package_name]
        else:
            if package_name not in config_data["packages"]:
                config_data["packages"][package_name] = {}

    with open(config_path, "w") as f:
        json.dump(config_data, f, indent=2)
        f.write("\n")


def template_metadata(relative_dir: str) -> Dict[str, Any]:
    """Load node specific template metadata.

    Returns:
        Dictionary of metadata. Includes the entire parsed contents of the package.json file if
        present. Other expected fields:
        * quickstart (str): Contents of the quickstart snippet if available; otherwise, ""
        * samples (List[Dict[str, str]]): List of available samples. See synthtool.gcp.samples.all_samples()
    """
    metadata = {}
    try:
        metadata = read_metadata(relative_dir)
    except FileNotFoundError:
        pass

    all_samples = samples.all_samples([str(Path(relative_dir, "samples/**/*.js"))])

    for sample in all_samples:
        rel_file_path = re.search(PACKAGE_DIRECTORIES_REGEX, sample["file"])
        if rel_file_path:
            sample["file"] = rel_file_path.group()

    # Exclude files in samples/test, samples/foo/test, etc.
    all_samples = list(filter(lambda s: "test/" not in s["file"], all_samples))

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
    return re.findall(r"\{\s*(\w+Client)\s*\}", content)


def generate_index_ts(
    versions: List[str],
    default_version: str,
    relative_dir: str,
    year: str,
    is_esm=False,
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
        (Path(relative_dir) / Path("src") / default_version / "index.ts")
        if not is_esm
        else (
            Path(relative_dir)
            / Path("esm")
            / Path("src")
            / default_version
            / "index.ts"
        )
    )
    clients = extract_clients(versioned_index_ts_path)
    if not clients:
        err_msg = f"No client is exported in the default version's({default_version}) index.ts ."
        logger.error(err_msg)
        raise AttributeError(err_msg)

    # compose template directory
    template_path = (
        (
            Path(__file__).parent.parent
            / "gcp"
            / "templates"
            / "node_mono_repo_split_library"
        )
        if not is_esm
        else (
            Path(__file__).parent.parent
            / "gcp"
            / "templates"
            / "node_esm_mono_repo_split_library"
        )
    )

    template_loader = FileSystemLoader(searchpath=str(template_path))
    template_env = Environment(loader=template_loader, keep_trailing_newline=True)
    TEMPLATE_FILE = "index.ts.j2"
    index_template = template_env.get_template(TEMPLATE_FILE)
    # render index.ts content
    output_text = index_template.render(
        versions=versions, default_version=default_version, clients=clients, year=year
    )
    index_ts_path = (
        Path(relative_dir, "src/index.ts").resolve()
        if not is_esm
        else Path(relative_dir, "esm", "src/index.ts").resolve()
    )
    with open(Path(relative_dir, index_ts_path).resolve(), "w") as fh:
        fh.write(output_text)
    logger.info("successfully generate `src/index.ts`")


def install(hide_output=False):
    """
    Installs all dependencies for the current Node.js library.
    """
    logger.debug("Installing dependencies...")
    shell.run(["npm", "install"], hide_output=hide_output)


def typeless_samples_hermetic(hide_output=False):
    """
    Converts TypeScript samples in the current Node.js library
    to JavaScript samples. Run this step before fix() and friends.
    Assumes that typeless-sample-bot is already installed in a well
    known location on disk (node_modules/.bin).

    This is currently an optional, opt-in part of an individual repo's
    OwlBot.py, and must be called from there before calling owlbot_main.
    """
    logger.debug("Run typeless sample bot")
    shell.run(
        [
            f"{_TOOLS_DIRECTORY}/node_modules/.bin/typeless-sample-bot",
            "--outputpath",
            "samples",
            "--targets",
            "samples",
            "--recursive",
        ],
        check=False,
        hide_output=hide_output,
    )


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
    is already installed in a well known location on disk (node_modules/.bin).
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


def compile_protos(hide_output=False, is_esm=False):
    """
    Compiles protos into .json, .js, and .d.ts files using
    compileProtos script from google-gax.
    """
    logger.debug("Compiling protos...")
    command = (
        ["npx", "compileProtos", "src"]
        if not is_esm
        else ["npx", "compileProtos", "esm/src", "--esm"]
    )
    shell.run(command, hide_output=hide_output)


def compile_protos_hermetic(relative_dir, is_esm=False, hide_output=False):
    """
    Compiles protos into .json, .js, and .d.ts files using
    compileProtos script from google-gax. Assumes that compileProtos
    is already installed in a well known location on disk (node_modules/.bin).
    """
    logger.debug("Compiling protos...")
    command = (
        [f"{_TOOLS_DIRECTORY}/node_modules/.bin/compileProtos", "src"]
        if not is_esm
        else [f"{_TOOLS_DIRECTORY}/node_modules/.bin/compileProtos", "esm/src", "--esm"]
    )
    shell.run(
        command,
        cwd=relative_dir,
        check=True,
        hide_output=hide_output,
    )


def postprocess_gapic_library(hide_output=False, is_esm=False):
    logger.debug("Post-processing GAPIC library...")
    install(hide_output=hide_output)
    fix(hide_output=hide_output)
    compile_protos(hide_output=hide_output, is_esm=is_esm)
    logger.debug("Post-processing completed")


def postprocess_gapic_library_hermetic(relative_dir, hide_output=False, is_esm=False):
    logger.debug("Post-processing GAPIC library...")
    fix_hermetic(relative_dir, hide_output=hide_output)
    compile_protos_hermetic(relative_dir, hide_output=hide_output, is_esm=is_esm)
    logger.debug("Post-processing completed")


default_staging_excludes = ["package.json", "src/index.ts", "esm/src/index.ts"]
default_templates_excludes: List[str] = []


def _noop(library: Path) -> None:
    pass


def get_destination_folder(package_name: str, base_dir: Path) -> Optional[str]:
    """
    Finds the destination folder (e.g. 'packages', 'handwritten') for a given package.
    It searches for a directory with the package name in all subdirectories of the current directory.
    """
    for path in base_dir.glob(f"*/{package_name}"):
        if path.is_dir() and path.parent.name != "owl-bot-staging":
            return path.parent.name
    return None


def find_owlbot_dirs_in_sub_dir(
    base_dir: Path,
    sub_dir: str,
    packages_to_exclude: List[str],
    search_for_changed_files: bool,
) -> List[str]:
    owlbot_dirs = []
    for path_object in base_dir.glob(f"{sub_dir}/**/.OwlBot.yaml"):
        if path_object.is_file() and not re.search(
            "(?:% s)" % "|".join(packages_to_exclude), str(Path(path_object))
        ):
            if search_for_changed_files:
                if (
                    subprocess.run(
                        [
                            "git",
                            "diff",
                            "--quiet",
                            "main...",
                            Path(path_object).parents[0],
                        ]
                    ).returncode
                    == 1
                ):
                    owlbot_dirs.append(str(Path(path_object).parents[0]))
            else:
                owlbot_dirs.append(str(Path(path_object).parents[0]))
    return owlbot_dirs


def walk_through_owlbot_dirs(dir: Path, search_for_changed_files: bool):
    """
    Walks through all API packages in google-cloud-node/packages

    Returns:
    A list of client libs
    """
    owlbot_dirs = []
    packages_to_exclude = [
        r"packages/gapic-node-processing/templates/bootstrap-templates",
        r"node_modules",
    ]
    if search_for_changed_files:
        try:
            # Need to run this step first in the post processor since we only clone
            # the branch that the PR is on in the Docker container
            output = subprocess.run(
                ["git", "fetch", "origin", "main:main", "--deepen=200"]
            )
            output.check_returncode()
        except subprocess.CalledProcessError as e:
            if e.returncode == 128:
                logger.info(f"Error: ${e.output}; skipping fetching main")
            else:
                raise e
    for sub_dir in PACKAGE_DIRECTORIES:
        owlbot_dirs.extend(
            find_owlbot_dirs_in_sub_dir(
                dir, sub_dir, packages_to_exclude, search_for_changed_files
            )
        )
    for path_object in dir.glob("owl-bot-staging/*"):
        package_name = Path(path_object).name
        destination_folder = get_destination_folder(package_name, dir)
        if destination_folder is None:
            raise RuntimeError(f"Can't find package {package_name} in subdirectories")
        owlbot_dirs.append(
            f"{Path(path_object).parents[1]}/{destination_folder}/{package_name}"
        )
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

    # This is the "old" behavior that only applies to the handwritten libraries (that haven't yet been migrated to the new post-processing structure)
    if "handwritten" in relative_dir:
        if staging_excludes is None:
            staging_excludes = default_staging_excludes
        if templates_excludes is None:
            templates_excludes = default_templates_excludes

        logging.basicConfig(level=logging.DEBUG)
        # Load the default version defined in .repo-metadata.json.
        default_version = json.load(
            open(Path(relative_dir, ".repo-metadata.json").resolve(), "rt")
        ).get("default_version")
        is_esm = False
        src = Path(Path(relative_dir), "src").resolve()
        source_location = "build/src"
        if (Path(Path(relative_dir), "esm", "src").resolve()).is_dir():
            is_esm = True
            src = Path(Path(relative_dir), "esm", "src").resolve()
            source_location = "build/esm/src"
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
            versions = [v.name for v in src.iterdir() if v.is_dir()]
            # Reorder the versions so the default version always comes last.
            versions = [v for v in versions if v != default_version] + [default_version]
            logger.info(f"Collected versions ${versions} from ${src}")

        common_templates = gcp.CommonTemplates(template_path)
        common_templates.excludes.extend(templates_excludes)
        if default_version:
            templates = common_templates.node_mono_repo_library(
                relative_dir=relative_dir,
                source_location=source_location,
                versions=versions,
                default_version=default_version,
                is_esm=is_esm,
            )
            s_copy([templates], destination=relative_dir, excludes=templates_excludes)
            postprocess_gapic_library_hermetic(relative_dir=relative_dir, is_esm=is_esm)
        else:
            templates = common_templates.node_mono_repo_library(
                relative_dir=relative_dir, source_location=source_location
            )
            s_copy([templates], destination=relative_dir, excludes=templates_excludes)
    # This is the "new" behavior that applies to libraries that have been migrated to the new post-processor (every gapic layer)
    else:
        staging = Path("owl-bot-staging", Path(relative_dir).name).resolve()
        s_copy = transforms.move
        if staging.is_dir():
            print(f"Entering staging copying ${staging} to {relative_dir}")
            # _tracked_paths.add(staging)
            s_copy([staging], destination=relative_dir)
            # The staging directory should never be merged into the main branch.
            shutil.rmtree(staging)

        print(f"Entering post-processing for {relative_dir}")
        shell.run(
            [
                "node",
                "/synthtool/synthtool/languages/node-monorepo-newprocess.js",
                Path(relative_dir).resolve(),
            ]
        )
        return


def owlbot_entrypoint(
    specified_owlbot_dirs: Optional[List[str]] = None,
    template_path: Optional[Path] = None,
    staging_excludes: Optional[List[str]] = None,
    templates_excludes: Optional[List[str]] = None,
    patch_staging: Callable[[Path], None] = _noop,
):
    if specified_owlbot_dirs:
        for dir in specified_owlbot_dirs:
            owlbot_py_file_path = hasOwlBotPy(dir)
            if owlbot_py_file_path:
                system(f"python3 {owlbot_py_file_path}")
            else:
                owlbot_main(
                    dir,
                    template_path,
                    staging_excludes,
                    templates_excludes,
                    patch_staging,
                )
    else:
        owlbot_dirs = walk_through_owlbot_dirs(
            Path.cwd(), search_for_changed_files=True
        )
        for dir in owlbot_dirs:
            owlbot_py_file_path = hasOwlBotPy(dir)
            if owlbot_py_file_path:
                system(f"python3 {owlbot_py_file_path}")
            else:
                owlbot_main(
                    dir,
                    template_path,
                    staging_excludes,
                    templates_excludes,
                    patch_staging,
                )
    if Path("release-please-config.json").is_file():
        write_release_please_config(
            walk_through_owlbot_dirs(Path.cwd(), search_for_changed_files=False)
        )


def hasOwlBotPy(dir):
    if Path(Path(dir, "owlbot.py").resolve()).exists():
        return Path(dir, "owlbot.py").resolve()


if __name__ == "__main__":
    # TODO: support iterating through 'all' packages
    # if you want to specify package names you wish to run in command line, i.e.,
    # python -m synthtool.languages.node_mono_repo packages/google-cloud-compute,packages/google-cloud-asset
    # if nothing is specified, it will default to only search for changed files
    if len(sys.argv) > 1:
        specified_owlbot_dirs = (sys.argv[1]).split(",")
        owlbot_entrypoint(specified_owlbot_dirs=specified_owlbot_dirs)
    else:
        owlbot_entrypoint()
