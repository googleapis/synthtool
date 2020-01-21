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

from pathlib import Path
from typing import Optional, Union
import os
import tempfile

from synthtool import _tracked_paths
from synthtool import log
from synthtool import metadata
from synthtool import shell
from synthtool.sources import git

GOOGLEAPIS_URL: str = git.make_repo_clone_url("googleapis/googleapis")
GOOGLEAPIS_PRIVATE_URL: str = git.make_repo_clone_url("googleapis/googleapis-private")
LOCAL_GOOGLEAPIS: Optional[str] = os.environ.get("SYNTHTOOL_GOOGLEAPIS")


class GAPICBazel:
    """A synthtool component that can produce libraries using bazel build.
    """

    def __init__(self):
        self._ensure_dependencies_installed()
        self._googleapis = None
        self._googleapis_private = None

    def py_library(self, service: str, version: str, **kwargs) -> Path:
        return self._generate_code(service, version, "python", **kwargs)

    def go_library(self, service: str, version: str, **kwargs) -> Path:
        return self._generate_code(service, version, "go", **kwargs)

    def node_library(self, service: str, version: str, **kwargs) -> Path:
        return self._generate_code(service, version, "nodejs", **kwargs)

    def csharp_library(self, service: str, version: str, **kwargs) -> Path:
        return self._generate_code(service, version, "csharp", **kwargs)

    def php_library(self, service: str, version: str, **kwargs) -> Path:
        return self._generate_code(service, version, "php", **kwargs)

    def java_library(self, service: str, version: str, **kwargs) -> Path:
        return self._generate_code(service, version, "java", **kwargs)

    def ruby_library(self, service: str, version: str, **kwargs) -> Path:
        return self._generate_code(service, version, "ruby", **kwargs)

    def _generate_code(
        self,
        service: str,
        version: str,
        language: str,
        *,
        private: bool = False,
        proto_path: Union[str, Path] = None,
        output_dir: Union[str, Path] = None,
        bazel_target: str = None,
    ):
        # Determine which googleapis repo to use
        if not private:
            googleapis = self._clone_googleapis()
        else:
            googleapis = self._clone_googleapis_private()

        # Sanity check: We should have a googleapis repo; if we do not,
        # something went wrong, and we should abort.
        if googleapis is None:
            raise RuntimeError(
                f"Unable to generate {service}, the googleapis repository"
                "is unavailable."
            )

        # Determine where the protos we are generating actually live.
        # We can sometimes (but not always) determine this from the service
        # and version; in other cases, the user must provide it outright.
        if proto_path:
            proto_path = Path(proto_path)
            if proto_path.is_absolute():
                proto_path = proto_path.relative_to("/")
        else:
            proto_path = Path("google/cloud") / service / version

        # Determine bazel target based on per-language patterns
        # Java:    google-cloud-{{assembly_name}}-{{version}}-java
        # Go:      gapi-cloud-{{assembly_name}}-{{version}}-go
        # Python:  {{assembly_name}}-{{version}}-py
        # PHP:     google-cloud-{{assembly_name}}-{{version}}-php
        # Node.js: {{assembly_name}}-{{version}}-nodejs
        # Ruby:    google-cloud-{{assembly_name}}-{{version}}-ruby
        # C#:      google-cloud-{{assembly_name}}-{{version}}-csharp
        if bazel_target is None:
            parts = list(proto_path.parts)
            while len(parts) > 0 and parts[0] != "google":
                parts.pop(0)
            if len(parts) == 0:
                raise RuntimeError(
                    f"Cannot determine bazel_target from proto_path {proto_path}."
                    "Please set bazel_target explicitly."
                )
            if language == "python":
                suffix = f"{service}-{version}-py"
            elif language == "nodejs":
                suffix = f"{service}-{version}-nodejs"
            elif language == "go":
                suffix = f"gapi-{'-'.join(parts[1:])}-go"
            else:
                suffix = f"{'-'.join(parts)}-{language}"
            bazel_target = f"//{os.path.sep.join(parts)}:{suffix}"

        # Sanity check: Do we have protos where we think we should?
        if not (googleapis / proto_path).exists():
            raise FileNotFoundError(
                f"Unable to find directory for protos: {(googleapis / proto_path)}."
            )
        if not tuple((googleapis / proto_path).glob("*.proto")):
            raise FileNotFoundError(
                f"Directory {(googleapis / proto_path)} exists, but no protos found."
            )
        if not (googleapis / proto_path / "BUILD.bazel"):
            raise FileNotFoundError(
                f"File {(googleapis / proto_path / 'BUILD.bazel')} does not exist."
            )

        # Ensure the desired output directory exists.
        # If none was provided, create a temporary directory.
        if not output_dir:
            output_dir = tempfile.mkdtemp()
        output_dir = Path(output_dir).resolve()

        # Let's build some stuff now.
        cwd = os.getcwd()
        os.chdir(str(googleapis))

        bazel_run_args = ["bazel", "build", bazel_target]

        log.debug(f"Generating code for: {proto_path}.")
        shell.run(bazel_run_args)

        # We've got tar file!
        # its location: bazel-bin/google/cloud/language/v1/language-v1-nodejs.tar.gz
        # bazel_target:         //google/cloud/language/v1:language-v1-nodejs
        tar_file = (
            f"bazel-bin{os.path.sep}{bazel_target[2:].replace(':', os.path.sep)}.tar.gz"
        )

        tar_run_args = [
            "tar",
            "-C",
            str(output_dir),
            "--strip-components=1",
            "-xzf",
            tar_file,
        ]
        shell.run(tar_run_args)

        os.chdir(cwd)

        # Sanity check: Does the output location have code in it?
        # If not, complain.
        if not tuple(output_dir.iterdir()):
            raise RuntimeError(
                f"Code generation seemed to succeed, but {output_dir} is empty."
            )

        # Huzzah, it worked.
        log.success(f"Generated code into {output_dir}.")

        # Record this in the synthtool metadata.
        metadata.add_client_destination(
            source="googleapis" if not private else "googleapis-private",
            api_name=service,
            api_version=version,
            language=language,
            generator="bazel",
        )

        _tracked_paths.add(output_dir)
        return output_dir

    def _clone_googleapis(self):
        if self._googleapis is not None:
            return self._googleapis

        if LOCAL_GOOGLEAPIS:
            self._googleapis = Path(LOCAL_GOOGLEAPIS).expanduser()
            log.debug(f"Using local googleapis at {self._googleapis}")

        else:
            log.debug("Cloning googleapis.")
            self._googleapis = git.clone(GOOGLEAPIS_URL)

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
            self._googleapis_private = git.clone(GOOGLEAPIS_PRIVATE_URL)

        return self._googleapis_private

    def _ensure_dependencies_installed(self):
        log.debug("Ensuring dependencies.")

        dependencies = ["bazel", "zip", "unzip", "tar"]
        failed_dependencies = []
        for dependency in dependencies:
            return_code = shell.run(["which", dependency], check=False).returncode
            if return_code:
                failed_dependencies.append(dependency)

        if failed_dependencies:
            raise EnvironmentError(
                f"Dependencies missing: {', '.join(failed_dependencies)}"
            )
