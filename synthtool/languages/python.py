# Copyright 2019 Google LLC
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

import re
import sys

import json
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional
import yaml

import synthtool as s
from synthtool import _tracked_paths, log, shell
from synthtool.gcp.common import CommonTemplates, detect_versions
from synthtool.sources import templates

PathOrStr = templates.PathOrStr

IGNORED_VERSIONS: List[str] = []

SAMPLES_TEMPLATE_PATH = Path(CommonTemplates()._template_root) / "python_samples"

NOTEBOOK_TEMPLATE_PATH = (
    Path(CommonTemplates()._template_root) / "python_notebooks_testing_pipeline"
)


def _get_help(filename: str) -> str:
    """Function used by sample readmegen"""
    return shell.run([sys.executable, filename, "--help"]).stdout


def _get_sample_readme_metadata(sample_dir: Path) -> dict:
    sample_readme = sample_dir / "README.rst.in"

    sample_metadata = {}
    if sample_readme.exists():
        requirements = str(Path(sample_dir / "requirements.txt").resolve())
        log.debug(
            f"Installing requirements at {requirements} to generate {sample_readme}"
        )
        shell.run([sys.executable, "-m", "pip", "install", "-r", requirements])

        with open(sample_readme) as f:
            sample_metadata = yaml.load(f, Loader=yaml.SafeLoader)
        for sample in sample_metadata["samples"]:
            # add absolute path to metadata so `python foo.py --help` succeeds
            sample["abs_path"] = Path(sample_dir / (sample["file"])).resolve()

    return sample_metadata


def python_notebooks_testing_pipeline() -> None:
    in_client_library = Path("owlbot.py").exists()
    if in_client_library:
        excludes: List[str] = []
        _tracked_paths.add(NOTEBOOK_TEMPLATE_PATH)
        s.copy([NOTEBOOK_TEMPLATE_PATH], excludes=excludes)


def py_samples(
    *,
    root: Optional[PathOrStr] = None,
    skip_readmes: bool = False,
    files_to_exclude: List[str] = [],
) -> None:
    """
    Find all samples projects and render templates.
    Samples projects always have a 'requirements.txt' file and may also have
    README.rst.in

    Args:
        root (Union[Path, str]): The samples directory root.
        skip_readmes (bool): If true, do not generate readmes.
        files_to_exclude(List[str]): defaults to empty, but if present, adds files to excludes list
    """
    in_client_library = Path("samples").exists() and Path("setup.py").exists()
    if root is None:
        if in_client_library:
            root = "samples"
        else:
            root = "."

    excludes = files_to_exclude

    # todo(kolea2): temporary exclusion until samples are ready to be migrated to new format
    excludes.append("README.md")

    # TODO(busunkim): Readmegen is disabled as it requires installing the sample
    # requirements in Synthtool. Sample Readmegen should be refactored to stop
    # relying on the output of `python sample.py --help`
    skip_readmes = True
    if skip_readmes:
        excludes.append("README.rst")
    t = templates.TemplateGroup(SAMPLES_TEMPLATE_PATH, excludes=excludes)

    t.env.globals["get_help"] = _get_help  # for sample readmegen

    for req in Path(root).glob("**/requirements.txt"):
        sample_project_dir = req.parent
        log.info(f"Generating templates for samples project '{sample_project_dir}'")

        excludes.append("**/*tmpl*")  # .tmpl. files are partial templates
        sample_readme_metadata: Dict[str, Any] = {}
        if not skip_readmes:
            sample_readme_metadata = _get_sample_readme_metadata(sample_project_dir)
            # Don't generate readme if there's no metadata
            if sample_readme_metadata == {}:
                excludes.append("**/README.rst")

        if Path(sample_project_dir / "noxfile_config.py").exists():
            # Don't overwrite existing noxfile configs
            excludes.append("**/noxfile_config.py")

        result = t.render(subdir=sample_project_dir, **sample_readme_metadata)
        _tracked_paths.add(result)
        s.copy([result], excludes=excludes)


def owlbot_main() -> None:
    """Copies files from staging and template directories into current working dir.

    When there is no owlbot.py file, run this function instead.

    Depends on owl-bot copying into a staging directory, so your .Owlbot.yaml should
    look a lot like this:

        docker:
            image: docker pull gcr.io/cloud-devrel-public-resources/owlbot-python:latest

        deep-remove-regex:
            - /owl-bot-staging

        deep-copy-regex:
            - source: /google/cloud/video/transcoder/(.*)/.*-nodejs/(.*)
              dest: /owl-bot-staging/$1/$2

    Also, this function requires a default_version in your .repo-metadata.json.  Ex:
        "default_version": "v1",
    """

    clean_up_generated_samples = True

    try:
        # Load the default version defined in .repo-metadata.json.
        default_version = json.load(open(".repo-metadata.json", "rt")).get(
            "default_version"
        )
    except FileNotFoundError:
        default_version = None

    if default_version:
        for library in s.get_staging_dirs(default_version):
            if clean_up_generated_samples:
                shutil.rmtree("samples/generated_samples", ignore_errors=True)
                clean_up_generated_samples = False
            s.move([library], excludes=["setup.py", "README.rst", "docs/index.rst"])
        s.remove_staging_dirs()

        templated_files = CommonTemplates().py_library(
            microgenerator=True,
            versions=detect_versions(path="./google", default_first=True),
        )
        s.move(
            [templated_files], excludes=[".coveragerc"]
        )  # the microgenerator has a good coveragerc file

        py_samples(skip_readmes=True)

        # run format nox session for all directories which have a noxfile
        for noxfile in Path(".").glob("**/noxfile.py"):
            s.shell.run(["nox", "-s", "format"], cwd=noxfile.parent, hide_output=False)


if __name__ == "__main__":
    owlbot_main()
