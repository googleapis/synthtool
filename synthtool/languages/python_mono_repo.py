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
import synthtool as s
import synthtool.gcp as gcp


def create_gapic_version_py(package_dir: str):
    """
    Create a version file `gapic_version.py` if it doesn't exist.

    Args:
        package_dir (str): path to the directory for a specific package. For example
            'packages/google-cloud-video-transcoder'
    """
    sub_directory_to_gapic = Path(package_dir).name.replace("-", "/")
    gapic_version_path = Path(
        f"{package_dir}/{sub_directory_to_gapic}/gapic_version.py"
    )

    gapic_version_text = """# -*- coding: utf-8 -*-
# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# x-release-please-start-version
__version__ = "0.1.0"
# x-release-please-end
"""

    if not gapic_version_path.exists():
        with open(gapic_version_path, "w") as f:
            f.write(gapic_version_text)


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
        default_version = None

    if default_version:
        for library in s.get_staging_dirs(
            default_version, f"owl-bot-staging/{Path(package_dir).name}"
        ):
            if clean_up_generated_samples:
                shutil.rmtree(
                    f"{package_dir}/samples/generated_samples", ignore_errors=True
                )
                clean_up_generated_samples = False
            s.move([library], package_dir, excludes=["**/gapic_version.py"])
        s.remove_staging_dirs()

        templated_files = gcp.CommonTemplates().py_mono_repo_library(
            relative_dir=f"packages/{Path(package_dir).name}",
            microgenerator=True,
            default_python_version="3.9",
            unit_test_python_versions=["3.7", "3.8", "3.9", "3.10"],
            cov_level=100,
            versions=gcp.common.detect_versions(
                path=f"{package_dir}/google", default_first=True
            ),
        )
        s.move([templated_files], package_dir)

        # create gapic_version.py if it doesn't exist
        create_gapic_version_py(package_dir)

        # create symlink docs/README.rst if it doesn't exist
        create_symlink_docs_readme(package_dir)

        # create CHANGELOG.md and symlink to docs/CHANGELOG.md if it doesn't exist
        create_changelog_and_symlink_to_docs_changelog(package_dir)

        # run format nox session for all directories which have a noxfile
        for noxfile in Path(".").glob(
            f"packages/{Path(package_dir).name}/**/noxfile.py"
        ):
            s.shell.run(["nox", "-s", "format"], cwd=noxfile.parent, hide_output=False)


if __name__ == "__main__":
    owlbot_dirs = walk_through_owlbot_dirs(Path.cwd())
    for package_dir in owlbot_dirs:
        owlbot_main(package_dir)
