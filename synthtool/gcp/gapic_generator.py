from pathlib import Path
import tempfile
import platform

from synthtool import _tracked_paths
from synthtool import log
from synthtool import shell
from synthtool.sources import git


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

    def _generate_code(self, service, version, language,
                       config_path=None, artman_output_name=None):
        # map the language to the artman argument and subdir of genfiles
        GENERATE_FLAG_LANGUAGE = {
            'python': ('python_gapic', 'python'),
            'nodejs': ('nodejs_gapic', 'js'),
            'ruby': ('ruby_gapic', 'ruby'),
        }

        if language not in GENERATE_FLAG_LANGUAGE:
            raise ValueError("provided language unsupported")

        gapic_arg, gen_language = GENERATE_FLAG_LANGUAGE[language]

        # Ensure docker image
        log.debug("Pulling artman docker image.")
        shell.run(['docker', 'pull', 'googleapis/artman:0.10.1'])

        # Run the code generator.
        # $ artman --config path/to/artman_api.yaml generate python_gapic
        if config_path is None:
            config_path = (
                Path('google/cloud') / service
                / f"artman_{service}_{version}.yaml")
        else:
            config_path = Path('google/cloud') / service / Path(config_path)

        if not (self.googleapis/config_path).exists():
            raise FileNotFoundError(
                f"Unable to find configuration yaml file: {config_path}.")

        subprocess_args = ['artman', '--config', config_path, 'generate',
                           gapic_arg]
        log.info(f"Running generator.")
        result = shell.run(subprocess_args, cwd=self.googleapis)

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
        log.debug("Ensuring dependencies")

        dependencies = ['docker', 'git', 'artman']
        failed_dependencies = []
        for dependency in dependencies:
            return_code = shell.run(
                ['which', dependency], check=False).returncode
            if return_code:
                failed_dependencies.append(dependency)

        if failed_dependencies:
            raise EnvironmentError(
                f"Dependencies missing: {', '.join(failed_dependencies)}")

        shell.run(['docker', 'pull', 'googleapis/artman:0.11.0'])

        # TODO: Install artman in a virtualenv.
