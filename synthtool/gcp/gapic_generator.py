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
import venv

from synthtool import _tracked_paths
from synthtool import cache
from synthtool import log
from synthtool import shell
from synthtool.sources import git

ARTMAN_VERSION = os.environ.get('SYNTHTOOL_ARTMAN_VERSION', 'latest')
ARTMAN_VENV = cache.get_cache_dir() / 'artman_venv'
GOOGLEAPIS_URL: str = 'git@github.com:googleapis/googleapis.git'
GOOGLEAPIS_PRIVATE_URL: str = (
    'git@github.com:googleapis/googleapis-private.git')


class GAPICGenerator:
    def __init__(self, private: bool = False):
        # Docker on mac by default cannot use the default temp file location
        # instead use the more standard *nix /tmp location\
        if platform.system() == 'Darwin':
            tempfile.tempdir = '/tmp'

        self._ensure_dependencies_installed()
        self._install_artman()

        # clone google apis to temp
        # git clone git@github.com:googleapis/googleapis.git
        if not private:
            googleapis_url = GOOGLEAPIS_URL
        else:
            googleapis_url = GOOGLEAPIS_PRIVATE_URL
        self.googleapis = git.clone(googleapis_url)

    def py_library(self, service: str, version: str, **kwargs) -> Path:
        '''
        Generates the Python Library files using artman/GAPIC
        returns a `Path` object
        library: path to library. 'google/cloud/speech'
        version: version of lib. 'v1'
        '''
        return self._generate_code(service, version, 'python', **kwargs)

    def node_library(self, service: str, version: str, **kwargs) -> Path:
        return self._generate_code(service, version, 'nodejs', **kwargs)

    nodejs_library = node_library

    def ruby_library(self, service: str, version: str, **kwargs) -> Path:
        return self._generate_code(service, version, 'ruby', **kwargs)

    def php_library(self, service: str, version: str, **kwargs) -> Path:
        return self._generate_code(service, version, 'php', **kwargs)

    def _generate_code(self, service, version, language,
                       config_path=None, artman_output_name=None):
        # map the language to the artman argument and subdir of genfiles
        GENERATE_FLAG_LANGUAGE = {
            'python': ('python_gapic', 'python'),
            'nodejs': ('nodejs_gapic', 'js'),
            'ruby': ('ruby_gapic', 'ruby'),
            'php': ('php_gapic', 'php'),
        }

        if language not in GENERATE_FLAG_LANGUAGE:
            raise ValueError("provided language unsupported")

        gapic_arg, gen_language = GENERATE_FLAG_LANGUAGE[language]

        # Run the code generator.
        # $ artman --config path/to/artman_api.yaml generate python_gapic
        if config_path is None:
            config_path = (
                Path('google/cloud') / service
                / f"artman_{service}_{version}.yaml")
        elif Path(config_path).is_absolute():
            config_path = Path(config_path).relative_to('/')
        else:
            config_path = Path('google/cloud') / service / Path(config_path)

        if not (self.googleapis/config_path).exists():
            raise FileNotFoundError(
                f"Unable to find configuration yaml file: {config_path}.")

        log.info(f"Running generator for {config_path}.")
        result = shell.run([
            ARTMAN_VENV / 'bin' / 'artman',
            '--config', config_path, 'generate', gapic_arg],
            cwd=self.googleapis)

        if result.returncode:
            raise Exception(f"Failed to generate from {config_path}")

        # Expect the output to be in the artman-genfiles directory.
        # example: /artman-genfiles/python/speech-v1
        if artman_output_name is None:
            artman_output_name = f"{service}-{version}"
        genfiles_dir = self.googleapis/'artman-genfiles'/gen_language
        genfiles = genfiles_dir/artman_output_name

        if not genfiles.exists():
            raise FileNotFoundError(
                f"Unable to find generated output of artman: {genfiles}.")

        _tracked_paths.add(genfiles)
        return genfiles

    def _ensure_dependencies_installed(self):
        log.debug("Ensuring dependencies.")

        dependencies = ['docker', 'git']
        failed_dependencies = []
        for dependency in dependencies:
            return_code = shell.run(
                ['which', dependency], check=False).returncode
            if return_code:
                failed_dependencies.append(dependency)

        if failed_dependencies:
            raise EnvironmentError(
                f"Dependencies missing: {', '.join(failed_dependencies)}")


    def _install_artman(self):
        if not ARTMAN_VENV.exists():
            venv.main([str(ARTMAN_VENV)])

        if ARTMAN_VERSION != 'latest':
            version_specifier = f'=={ARTMAN_VERSION}'
        else:
            version_specifier = ''

        shell.run([
            ARTMAN_VENV / 'bin' / 'pip', 'install', '--upgrade',
            f'googleapis-artman{version_specifier}'])
        log.debug('Pulling artman image.')
        shell.run(['docker', 'pull', f'googleapis/artman:{ARTMAN_VERSION}'])
