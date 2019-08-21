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
import requests
import shutil
import subprocess
import yaml

from pathlib import Path
from typing import Optional

from synthtool import _tracked_paths
from synthtool import log
from synthtool import metadata
from synthtool import shell
from synthtool.gcp import artman
from synthtool.sources import git

GOOGLEAPIS_URL: str = git.make_repo_clone_url("googleapis/googleapis")
GOOGLEAPIS_PRIVATE_URL: str = git.make_repo_clone_url("googleapis/googleapis-private")
LOCAL_GOOGLEAPIS: Optional[str] = os.environ.get("SYNTHTOOL_GOOGLEAPIS")
LOCAL_GENERATOR: Optional[str] = os.environ.get("SYNTHTOOL_GENERATOR")


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
        include_protos=False,
        include_samples=False,
        generator_args=None,
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

        generator_dir = LOCAL_GENERATOR
        if generator_dir is not None:
            log.debug(f"Using local generator at {generator_dir}")

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

        if include_samples:
            if generator_args is None:
                generator_args = []
            # Add feature flag for generating code samples with code generator.
            generator_args.append("--dev_samples")

        output_root = self._artman.run(
            f"googleapis/artman:{artman.ARTMAN_VERSION}",
            googleapis,
            config_path,
            gapic_language_arg,
            generator_dir=generator_dir,
            generator_args=generator_args,
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

        # Get the *.protos files and put them in a protos dir in the output
        if include_protos:
            source_dir = googleapis / config_path.parent / version
            proto_files = source_dir.glob("**/*.proto")
            # By default, put the protos at the root in a folder named 'protos'.
            # Specific languages can be cased here to put them in a more language
            # appropriate place.
            proto_output_path = genfiles / "protos"
            if language == "python":
                # place protos alongsize the *_pb2.py files
                proto_output_path = genfiles / f"google/cloud/{service}_{version}/proto"
            os.makedirs(proto_output_path, exist_ok=True)

            for i in proto_files:
                log.debug(f"Copy: {i} to {proto_output_path / i.name}")
                shutil.copyfile(i, proto_output_path / i.name)
            log.success(f"Placed proto files into {proto_output_path}.")

        if include_samples:
            googleapis_service_dir = googleapis / config_path.parent
            self._include_samples(language, version, genfiles, googleapis_service_dir)

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

    def _include_samples(self, language, version, genfiles, googleapis_service_dir):
        """Include code samples and supporting resources in generated output.

        Resulting directory structure in generated output:
            samples/
            ├── resources
            │   └── file.csv
            └── v1/
                ├── samples.manifest.yaml
                ├── sample.py
                └── test/
                    └── sample.test.yaml

        Samples are included in the genfiles output of the generator.

        Sample tests are defined in googleapis:
            {service}/{version}/samples/*.test.yaml

        Sample resources are declared in {service}/sample_resources.yaml
        which includes a list of files with public gs:// URIs for download.

        Sample manifest is a generated file which defines invocation commands
        for each code sample (used by sample-tester to invoke samples).
        """

        samples_root_dir = genfiles / "samples"
        samples_resources_dir = samples_root_dir / "resources"
        samples_version_dir = samples_root_dir / version

        # Some languages capitalize their `V` prefix for version numbers
        if not samples_version_dir.is_dir():
            samples_version_dir = samples_root_dir / version.capitalize()

        # Do not proceed if genfiles does not include samples/{version} dir.
        if not samples_version_dir.is_dir():
            return None

        samples_test_dir = samples_version_dir / "test"
        samples_manifest_yaml = samples_test_dir / "samples.manifest.yaml"

        googleapis_samples_dir = googleapis_service_dir / version / "samples"
        googleapis_resources_yaml = googleapis_service_dir / "sample_resources.yaml"


        # Copy sample tests from googleapis {service}/{version}/samples/*.test.yaml
        # into generated output as samples/{version}/test/*.test.yaml
        test_files = googleapis_samples_dir.glob("**/*.test.yaml")
        os.makedirs(samples_test_dir, exist_ok=True)
        for i in test_files:
                log.debug(f"Copy: {i} to {samples_test_dir / i.name}")
                shutil.copyfile(i, samples_test_dir / i.name)

        # Download sample resources from sample_resources.yaml storage URIs.
        #
        #  sample_resources:
        #  - uri: gs://bucket/the/file/path.csv
        #    description: Description of this resource
        #
        # Code follows happy path. An error is desirable if YAML is invalid.
        if googleapis_resources_yaml.is_file():
            with open(googleapis_resources_yaml, "r") as f:
                resources_data = yaml.load(f, Loader=yaml.SafeLoader)
            resource_list = resources_data.get("sample_resources")
            for resource in resource_list:
                uri = resource.get("uri")
                if uri.startswith("gs://"):
                    uri = uri.replace("gs://", "https://storage.googleapis.com/")
                response = requests.get(uri, allow_redirects=True)
                download_path = samples_resources_dir / os.path.basename(uri)
                os.makedirs(samples_resources_dir, exist_ok=True)
                log.debug(f"Download {uri} to {download_path}")
                with open(download_path, "wb") as f:
                    f.write(response.content)

        # Generate manifest file at samples/{version}/test/samples.manifest.yaml
        # Includes a reference to every sample (via its "region tag" identifier)
        # along with structured instructions on how to invoke that code sample.
        relative_manifest_path = str(samples_manifest_yaml.relative_to(samples_root_dir))
        MANIFEST_GEN_LANGUAGE_ARGUMENTS = {
            "python": ["--bin=python3"],
            "nodejs": ["--bin=node"],
            "ruby": ["--bin=bundle exec ruby"],
            "php": ["--bin=php"]
        }
        manifest_arguments = ["gen-manifest"]
        manifest_arguments.extend(MANIFEST_GEN_LANGUAGE_ARGUMENTS[language])
        manifest_arguments.extend([f"--env={language}"])
        manifest_arguments.extend(["--chdir={@manifest_dir}/../.."])
        manifest_arguments.extend([f"--output={relative_manifest_path}"])
        for code_sample in samples_version_dir.glob("*"):
            sample_path = str(code_sample.relative_to(samples_root_dir))
            if os.path.isfile(code_sample):
                manifest_arguments.append(sample_path)
        try:
            log.debug(f"Writing samples manifest {manifest_arguments}")
            shell.run(manifest_arguments, cwd=samples_root_dir)
        except subprocess.CalledProcessError as exp:
            log.warning("gen-manifest failed (sample-tester may not be installed)")