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

import os
from pathlib import Path
from typing import Optional

from synthtool import _tracked_paths
from synthtool import log
from synthtool import metadata
from synthtool.gcp import artman
from synthtool.sources import git

GOOGLEAPIS_URL: str = git.make_repo_clone_url("googleapis/googleapis")
GOOGLEAPIS_PRIVATE_URL: str = git.make_repo_clone_url("googleapis/googleapis-private")
LOCAL_GOOGLEAPIS: Optional[str] = os.environ.get("SYNTHTOOL_GOOGLEAPIS")


class GAPICGenerator:
    def __init__(self):
        self._googleapis = None
        self._googleapis_private = None
        self._artman = artman.Artman()

    def py_library(self, service: str, version: str, **kwargs) -> Path:
        """
        Generates the Python Library files using artman/GAPIC
        returns a `Path` object
        library: path to library. 'google/cloud/speech'
        version: version of lib. 'v1'
        """
        return self._generate_code(service, version, "python", **kwargs)

    def node_library(self, service: str, version: str, **kwargs) -> Path:
        return self._generate_code(service, version, "nodejs", **kwargs)

    nodejs_library = node_library

    def ruby_library(self, service: str, version: str, **kwargs) -> Path:
        return self._generate_code(service, version, "ruby", **kwargs)

    def php_library(self, service: str, version: str, **kwargs) -> Path:
        return self._generate_code(service, version, "php", **kwargs)

    def java_library(self, service: str, version: str, **kwargs) -> Path:
        return self._generate_code(service, version, "java", **kwargs)

    def _generate_code(
        self,
        service,
        version,
        language,
        config_path=None,
        artman_output_name=None,
        private=False,
    ):
        # map the language to the artman argument and subdir of genfiles
        GENERATE_FLAG_LANGUAGE = {
            "python": ("python_gapic", "python"),
            "nodejs": ("nodejs_gapic", "js"),
            "ruby": ("ruby_gapic", "ruby"),
            "php": ("php_gapic", "php"),
            "java": ("java_gapic", "java"),
        }

        if language not in GENERATE_FLAG_LANGUAGE:
            raise ValueError("provided language unsupported")

        gapic_language_arg, gen_language = GENERATE_FLAG_LANGUAGE[language]

        # Determine which googleapis repo to use
        if not private:
            googleapis = self._clone_googleapis()
        else:
            googleapis = self._clone_googleapis_private()

        if googleapis is None:
            raise RuntimeError(
                f"Unable to generate {config_path}, the googleapis repository"
                "is unavailable."
            )

        # Run the code generator.
        # $ artman --config path/to/artman_api.yaml generate python_gapic
        if config_path is None:
            config_path = (
                Path("google/cloud") / service / f"artman_{service}_{version}.yaml"
            )
        elif Path(config_path).is_absolute():
            config_path = Path(config_path).relative_to("/")
        else:
            config_path = Path("google/cloud") / service / Path(config_path)

        if not (googleapis / config_path).exists():
            raise FileNotFoundError(
                f"Unable to find configuration yaml file: {(googleapis / config_path)}."
            )

        log.debug(f"Running generator for {config_path}.")

        output_root = self._artman.run(
            f"googleapis/artman:{artman.ARTMAN_VERSION}",
            googleapis,
            config_path,
            gapic_language_arg,
        )

        # Expect the output to be in the artman-genfiles directory.
        # example: /artman-genfiles/python/speech-v1
        if artman_output_name is None:
            artman_output_name = f"{service}-{version}"
        genfiles = output_root / gen_language / artman_output_name

        if not genfiles.exists():
            raise FileNotFoundError(
                f"Unable to find generated output of artman: {genfiles}."
            )

        log.success(f"Generated code into {genfiles}.")

        metadata.add_client_destination(
            source="googleapis" if not private else "googleapis-private",
            api_name=service,
            api_version=version,
            language=language,
            generator="gapic",
            config=str(config_path),
        )

        _tracked_paths.add(genfiles)
        return genfiles

    def _clone_googleapis(self):
        if self._googleapis is not None:
            return self._googleapis

        if LOCAL_GOOGLEAPIS:
            self._googleapis = Path(LOCAL_GOOGLEAPIS).expanduser()
            log.debug(f"Using local googleapis at {self._googleapis}")

        else:
            log.debug("Cloning googleapis.")
            self._googleapis = git.clone(GOOGLEAPIS_URL, depth=1)

        return self._googleapis

    def _clone_googleapis_private(self):
        if self._googleapis_private is not None:
            return self._googleapis_private

        if LOCAL_GOOGLEAPIS:
            self._googleapis_private = Path(LOCAL_GOOGLEAPIS).expanduser()
            log.debug(
                f"Using local googleapis at {self._googleapis_private} for googleapis-private"
            )

        else:
            log.debug("Cloning googleapis-private.")
            self._googleapis_private = git.clone(GOOGLEAPIS_PRIVATE_URL, depth=1)

        return self._googleapis_private
