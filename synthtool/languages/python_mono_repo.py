# Copyright 2022 Google LLC
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
import shutil
import synthtool
import synthtool.gcp as gcp
import yaml


def create_symlink_in_docs_dir(package_dir: str, filename: str):
    """Creates a symlink in the docs directory for <filename> pointing to ../<filename>
        using the package_dir specified as the base directory.

    Args:
        package_dir (str): path to the directory for a specific package. For example
            'packages/google-cloud-video-transcoder'
        working_dir (str): the absolute path to the directory where the link should be created
        filename (str): the name of the file to link
    """

    current_dir = os.getcwd()

    os.chdir(f"{package_dir}/docs")

    relative_path_to_docs_file = Path(filename)
    relative_path_to_file = Path(f"../{filename}")

    if relative_path_to_file.exists():
        if not relative_path_to_docs_file.exists():
            Path(relative_path_to_docs_file).symlink_to(relative_path_to_file)

    os.chdir(current_dir)


def create_symlink_docs_readme(package_dir: str):
    """Creates a symlink for docs/README.rst pointing to README.rst
        in the package_dir specified.

    Args:
        package_dir (str): path to the directory for a specific package. For example
            'packages/google-cloud-video-transcoder'
    """
    create_symlink_in_docs_dir(package_dir, "README.rst")


def create_changelog_and_symlink_to_docs_changelog(package_dir: str):
    """Creates a CHANGELOG.md in the package_dir specified if it
        doesn't exist and a symlink for docs/CHANGELOG.md pointing
        to CHANGELOG.md.

    Args:
        package_dir (str): path to the directory for a specific package. For example
            'packages/google-cloud-video-transcoder'
    """
    path_to_changelog = Path(f"{package_dir}/CHANGELOG.md")

    # Create a CHANGELOG.md file if it doesn't exist
    if not path_to_changelog.exists():
        with open(path_to_changelog, "w") as f:
            f.write("# Changelog")

    create_symlink_in_docs_dir(package_dir, "CHANGELOG.md")


def update_url_in_setup_py(package_dir: str):
    """Update the url in setup.py to point to the mono repo google-cloud-python

    Args:
        package_dir (str): path to the directory for a specific package. For example
            'packages/google-cloud-video-transcoder'
    """
    path_to_setup_py = Path(f"{package_dir}/setup.py")

    with open(path_to_setup_py, "r") as f:
        new_setup_py = []
        for line in f:
            if line.startswith("""url = \"https://github.com/googleapis/python-"""):
                new_setup_py.append(
                    """url = \"https://github.com/googleapis/google-cloud-python\"\n"""
                )
            else:
                new_setup_py.append(line)

    with open(path_to_setup_py, "w") as f:
        f.writelines(new_setup_py)


def apply_client_specific_post_processing(
    post_processing_dir: str, package_name: str
) -> None:
    """Applies client-specific post processing which exists in the Path `post_processing_dir`.
    This function is only called from `owlbot_main` when there is an `owl-bot-staging` folder
    which contains generated client library code. Re-running the script more than once is
    expected to be idempotent. The client-specific post processing YAML is in the following format:
    ```
        description: Verbose description about the need for the workaround.
        url: URL of the issue in gapic-generator-python tracking eventual removal of the workaround
        replacements:
          - replacement:
            paths: [<List of files where the replacement should occur relative to the monorepo root directory>]
            before: "The string to search for in the specified paths"
            after:  "The string to replace in the the specified paths",
            count: <integer indicating number of replacements that should have occurred across all files after the script is run>
    ```

    Note: The `paths` key above must only include paths for the same package so that the number of replacements
    made in a given package can be verified.

    Args:
        post_processing_dir (str): Path to the directory which contains YAML files which will
            be used to apply client-specific post processing, e.g. 'packages/<package_name>/scripts/client-post-processing'
            relative to the monorepo root directory.
        package_name (str): The name of the package where client specific post processing will be applied.
    """

    if Path(post_processing_dir).exists():
        for post_processing_path in Path(post_processing_dir).iterdir():
            with open(post_processing_path, "r") as post_processing_path_file:
                post_processing_json = yaml.safe_load(post_processing_path_file)
                all_replacements = post_processing_json["replacements"]
                # For each workaround related to the specified issue
                for replacement in all_replacements:
                    replacement_count = 0
                    number_of_paths_with_replacements = 0
                    # For each file that needs the workaround applied
                    for client_library_path in replacement["paths"]:
                        if package_name in client_library_path:
                            number_of_paths_with_replacements += 1
                            replacement_count += synthtool.replace(
                                client_library_path,
                                replacement["before"],
                                replacement["after"],
                            )
                            # Ensure idempotency by checking that subsequent calls won't
                            # trigger additional replacements within the same path
                            assert (
                                synthtool.replace(
                                    client_library_path,
                                    replacement["before"],
                                    replacement["after"],
                                )
                                == 0
                            )
                    if number_of_paths_with_replacements:
                        # Ensure that the numner of paths where a replacement occurred matches the number of paths.
                        assert number_of_paths_with_replacements == len(
                            replacement["paths"]
                        )
                        # Ensure that the total number of replacements matches the value specified in `count`
                        # for all paths in `replacement["paths"]`
                        assert replacement_count == replacement["count"]


def walk_through_owlbot_dirs(dir: Path):
    """
    Walks through all API packages in google-cloud-python/packages
    Returns:
    A list of client libs
    """
    owlbot_dirs = []
    for path_object in dir.glob("packages/**/.OwlBot.yaml"):
        if path_object.is_file():
            owlbot_dirs.append(str(Path(path_object).parents[0]))

    return owlbot_dirs


def owlbot_main(package_dir: str) -> None:
    """Copies files from staging and template directories into current working dir.

    When there is no owlbot.py file, run this function instead.

    Depends on owl-bot copying into a staging directory, so your .OwlBot.yaml should
    look a lot like this:

        deep-copy-regex:
            - source: /google/cloud/video/transcoder/(.*)/.*-py
              dest: /owl-bot-staging/google-cloud-video-transcoder/$1

    Also, this function requires a default_version in your .repo-metadata.json.  Ex:
        "default_version": "v1",

    Args:
        package_dir: relative path to the directory for a specific package. For example
            packages/google-cloud-video-transcoder
    """

    clean_up_generated_samples = True

    try:
        # Load the default version defined in .repo-metadata.json.
        default_version = json.load(
            open(f"{Path(package_dir)}/.repo-metadata.json", "rt")
        ).get("default_version")
    except FileNotFoundError:
        raise Exception("Could not find the default version")

    package_name = Path(package_dir).name

    if Path(f"owl-bot-staging/{package_name}").exists():
        for library in synthtool.get_staging_dirs(
            default_version, f"owl-bot-staging/{package_name}"
        ):
            if clean_up_generated_samples:
                shutil.rmtree(
                    f"{package_dir}/samples/generated_samples", ignore_errors=True
                )
                clean_up_generated_samples = False
            synthtool.move([library], package_dir, excludes=[])

        templated_files = gcp.CommonTemplates().py_mono_repo_library(
            relative_dir=f"packages/{package_name}",
            microgenerator=True,
            default_python_version="3.10",
            unit_test_python_versions=["3.7", "3.8", "3.9", "3.10", "3.11"],
            system_test_python_versions=["3.8", "3.9", "3.10", "3.11"],
            cov_level=100,
            versions=gcp.common.detect_versions(
                path=f"{package_dir}/google"
                if package_name.startswith("google")
                else f"{package_dir}/{package_name}",
                default_version=default_version,
                default_first=True,
            ),
        )
        synthtool.move([templated_files], package_dir)

        # create symlink docs/README.rst if it doesn't exist
        create_symlink_docs_readme(package_dir)

        # create CHANGELOG.md and symlink to docs/CHANGELOG.md if it doesn't exist
        create_changelog_and_symlink_to_docs_changelog(package_dir)

        # update the url in setup.py to point to google-cloud-python
        update_url_in_setup_py(package_dir)

        # run format nox session for all directories which have a noxfile
        for noxfile in Path(".").glob(f"packages/{package_name}/**/noxfile.py"):
            synthtool.shell.run(
                ["nox", "-s", "format"], cwd=noxfile.parent, hide_output=False
            )

        apply_client_specific_post_processing(
            f"packages/{package_name}/scripts/client-post-processing", package_name
        )


if __name__ == "__main__":
    owlbot_dirs = walk_through_owlbot_dirs(Path.cwd())
    for package_dir in owlbot_dirs:
        owlbot_main(package_dir)

    synthtool.remove_staging_dirs()
