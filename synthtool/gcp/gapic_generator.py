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
import tempfile
import platform
import subprocess
import venv

from synthtool import _tracked_paths
from synthtool import cache
from synthtool import log
from synthtool import shell
from synthtool.sources import git

ARTMAN_VERSION = os.environ.get("SYNTHTOOL_ARTMAN_VERSION", "latest")
ARTMAN_VENV = cache.get_cache_dir() / "artman_venv"
GOOGLEAPIS_URL: str = "git@github.com:googleapis/googleapis.git"
GOOGLEAPIS_PRIVATE_URL: str = ("git@github.com:googleapis/googleapis-private.git")


# Docker on mac by default cannot use the default temp file location
# instead use the more standard *nix /tmp location\
if platform.system() == "Darwin":
    tempfile.tempdir = "/tmp"


def _run_artman(image, root_dir, config, *args):
    """Executes artman command in the artman container.
    Args:
        root_dir: The input directory that will be mounted to artman docker
            container as local googleapis directory.
    Returns:
        The output directory with artman-generated files.
    """
    container_name = "artman-docker"
    output_dir = root_dir / "artman-genfiles"

    docker_cmd = [
        "docker",
        "run",
        "--name",
        container_name,
        "--rm",
        "-i",
        "-e",
        f"HOST_USER_ID={os.getuid()}",
        "-e",
        f"HOST_GROUP_ID={os.getgid()}",
        "-e",
        "RUNNING_IN_ARTMAN_DOCKER=True",
        "-v",
        f"{root_dir}:{root_dir}",
        "-v",
        f"{output_dir}:{output_dir}",
        "-w",
        root_dir,
        image,
        "/bin/bash",
        "-c",
    ]

    artman_command = " ".join(
        map(str, ["artman", "--local", "--config", config, "generate"] + list(args))
    )

    cmd = docker_cmd + [artman_command]

    shell.run(cmd, cwd=root_dir)

    return output_dir


class GAPICGenerator:
    def __init__(self):

        self._ensure_dependencies_installed()
        self._install_artman()
        self._clone_googleapis()

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
            googleapis = self.googleapis
        else:
            googleapis = self.googleapis_private

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
                f"Unable to find configuration yaml file: {config_path}."
            )

        log.debug(f"Running generator for {config_path}.")
        output_root = _run_artman(
            f"googleapis/artman:{ARTMAN_VERSION}",
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

        _tracked_paths.add(genfiles)
        return genfiles

    def _ensure_dependencies_installed(self):
        log.debug("Ensuring dependencies.")

        dependencies = ["docker", "git"]
        failed_dependencies = []
        for dependency in dependencies:
            return_code = shell.run(["which", dependency], check=False).returncode
            if return_code:
                failed_dependencies.append(dependency)

        if failed_dependencies:
            raise EnvironmentError(
                f"Dependencies missing: {', '.join(failed_dependencies)}"
            )

    def _install_artman(self):
        if not ARTMAN_VENV.exists():
            venv.main([str(ARTMAN_VENV)])

        if ARTMAN_VERSION != "latest":
            version_specifier = f"=={ARTMAN_VERSION}"
        else:
            version_specifier = ""

        shell.run(
            [
                ARTMAN_VENV / "bin" / "pip",
                "install",
                "--upgrade",
                f"googleapis-artman{version_specifier}",
            ]
        )
        log.debug("Pulling artman image.")
        shell.run(["docker", "pull", f"googleapis/artman:{ARTMAN_VERSION}"])

    def _clone_googleapis(self):
        log.debug("Cloning googleapis.")
        self.googleapis = git.clone(GOOGLEAPIS_URL, depth=1)

        try:
            self.googleapis_private = git.clone(GOOGLEAPIS_PRIVATE_URL, depth=1)
        except subprocess.CalledProcessError:
            log.warning(
                "Could not clone googleapis-private, you will not be able to "
                "generate private API versions!"
            )
