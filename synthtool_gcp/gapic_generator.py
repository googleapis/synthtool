from pathlib import Path
import tempfile
import platform

from synthtool import log
from synthtool import shell
from synthtool.sources import git


GOOGLEAPIS_URL: str = 'git@github.com:googleapis/googleapis.git'
GOOGLEAPIS_PRIVATE_URL: str = (
    'git@github.com:googleapis/googleapis-private.git')


class GAPICGenerator:
    def __init__(self, googleapis_url: str = GOOGLEAPIS_URL):
        # Docker on mac by default cannot use the default temp file location
        # instead use the more standard *nix /tmp location\
        if platform.system() == 'Darwin':
            tempfile.tempdir = '/tmp'

        self._ensure_dependencies_installed()

        # clone google apis to temp
        # git clone git@github.com:googleapis/googleapis.git
        self.googleapis = git.clone(googleapis_url)

    def py_library(self, service: str, version: str) -> Path:
        '''
        Generates the Python Library files using artman/GAPIC
        returns a `Path` object
        library: path to library. 'google/cloud/speech'
        version: version of lib. 'v1'
        '''
        return self._generate_code(service, version, 'python')

    def _generate_code(self, service, version, language,
                       artman_yaml_name=None, artman_output_name=None):
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
        log.debug("Pulling artman docker image")
        shell.run(['docker', 'pull', 'googleapis/artman:0.9.1'])

        # Run the code generator.
        # $ artman --config path/to/artman_api.yaml generate python_gapic
        if artman_yaml_name is None:
            artman_yaml_name = f"artman_{service}_{version}.yaml"
        artman_yaml = Path('google/cloud')/service/artman_yaml_name
        log.debug(f"artman yaml: {artman_yaml}")

        if not (self.googleapis/artman_yaml).exists():
            raise FileNotFoundError(
                f"Unable to find artman yaml file: {artman_yaml}")

        subprocess_args = ['artman', '--config', artman_yaml, 'generate',
                           gapic_arg]
        log.info(f"Running Artman: {subprocess_args}")
        result = shell.run(subprocess_args, cwd=self.googleapis)

        if result.returncode:
            raise Exception(f"Failed to generate {artman_yaml}")

        # Expect the output to be in the artman-genfiles directory.
        # example: /artman-genfiles/python/speech-v1
        if artman_output_name is None:
            artman_output_name = f"{service}-{version}"
        genfiles_dir = self.googleapis/'artman-genfiles'/gen_language
        genfiles = genfiles_dir/artman_output_name

        if not genfiles.exists():
            raise FileNotFoundError(
                f"Unable to find generated output of artman: {genfiles}")

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
