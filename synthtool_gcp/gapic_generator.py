from pathlib import Path
import subprocess
import tempfile
import logging
import platform


class GAPICGenerator:
    def __init__(self, googleapis_repo_location=None):
        self.logger = logging.getLogger('GAPICGenerator')

        # Docker on mac by default cannot use the default temp file location
        # instead use the more standard *nix /tmp location\
        if platform.system() == 'Darwin':
            tempfile.tempdir = '/tmp'

        self.logger.info("Ensuring dependencies")
        self._ensure_dependencies_installed()

        # clone google apis to temp
        # git clone git@github.com:googleapis/googleapis.git
        if not googleapis_repo_location:
            googleapis_repo_location = tempfile.mkdtemp()
        self.googleapis = Path(googleapis_repo_location)

        # Even if we provided a path, just try to clone. This will noop if it
        # exists.
        if not self.googleapis.exists():
            self.logger.info("clone googleapis/googleapis")
            subprocess.run(['git',
                            'clone',
                            'git@github.com:googleapis/googleapis.git',
                            self.googleapis],
                           stdout=subprocess.DEVNULL)
        else:
            # we aren't going to reclone, but we should pull.
            self.logger.info("pull googleapis/googleapis")
            subprocess.run(['git',
                            'pull'],
                           cwd=self.googleapis,
                           stdout=subprocess.DEVNULL)

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
        self.logger.info("Pulling artman docker image")
        subprocess.run(['docker', 'pull', 'googleapis/artman:0.9.1'],
                       stdout=subprocess.DEVNULL)

        # Run the code generator.
        # $ artman --config path/to/artman_api.yaml generate python_gapic
        if artman_yaml_name is None:
            artman_yaml_name = f"artman_{service}_{version}.yaml"
        artman_yaml = Path('google/cloud')/service/artman_yaml_name
        self.logger.info(f"artman yaml: {artman_yaml}")

        if not (self.googleapis/artman_yaml).exists():
            raise FileNotFoundError(
                f"Unable to find artman yaml file: {artman_yaml}")

        subprocess_args = ['artman', '--config', artman_yaml, 'generate',
                           'python_gapic']
        self.logger.info(f"Running Artman: {subprocess_args}")
        result = subprocess.run(subprocess_args,
                                stdout=subprocess.DEVNULL,
                                cwd=self.googleapis)

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
        dependencies = ['docker', 'git', 'artman']
        failed_dependencies = []
        for dependency in dependencies:
            return_code = subprocess.run(
                ['which', dependency],
                stdout=subprocess.DEVNULL).returncode
            if return_code:
                failed_dependencies.append(dependency)

        if failed_dependencies:
            raise EnvironmentError(
                f"Dependencies missing: {', '.join(failed_dependencies)}")
