# Copyright 2020 Google LLC
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

from autosynth.log import logger, LogCollector

from abc import ABC, abstractmethod
import subprocess
import os
import pathlib
import tempfile
import typing


class Executor(ABC):
    """An executor abstracts the handling of executing command line
    scripts and allows consolidating handling of the command's output.
    """

    @abstractmethod
    def execute(
        self,
        command: typing.List[str],
        log_file_path: pathlib.Path = None,
        environ: typing.Mapping[str, str] = None,
        cwd: str = None,
        check: bool = False,
    ) -> typing.Tuple[subprocess.CompletedProcess, str]:
        """Execute the provided command

        Arguments:
            command {typing.List[str]} -- The command provided as a list of string tokens.
            log_file_path {typing.Optional[pathlib.Path]} -- If provided, the output of
                the command should be written to this path.
            environ {typing.Optional[typing.Mapping[str, str]]} -- Map of environment
                variables to set. Defaults to the current environment.
            cwd {typing.Optional[str]} -- Working directory to run the command from.
                Defaults to the current working directory.
            check {bool} -- If true, will raise an exception on failure.

        Returns:
            typing.Tuple[subprocess.CompletedProcess, str] -- The first item of the tuple is
                the complete subprocess which  contains more metadata about the executed
                process. The second item of the tuple is the captured output.

        Throws:
            subprocess.CalledProcessError if the process fails and check=True is set.
        """
        pass

    def run(
        self,
        command: typing.List[str],
        log_file_path: pathlib.Path = None,
        environ: typing.Mapping[str, str] = None,
        cwd: str = None,
        check: bool = True,
    ) -> str:
        """Execute the provided command

        Arguments:
            command {typing.List[str]} -- The command provided as a list of string tokens.
            log_file_path {typing.Optional[pathlib.Path]} -- If provided, the output of
                the command should be written to this path.
            environ {typing.Optional[typing.Mapping[str, str]]} -- Map of environment
                variables to set. Defaults to the current environment.
            cwd {typing.Optional[str]} -- Working directory to run the command from.
                Defaults to the current working directory.
            check {bool} -- If true, will raise an exception on failure.

        Returns:
            str -- The captured output.

        Throws:
            subprocess.CalledProcessError if the process fails and check=True is set.
        """
        (_, output) = self.execute(
            command, log_file_path=log_file_path, environ=environ, cwd=cwd, check=check
        )
        return output


class LogCapturingExecutor(Executor):
    """This executor executes the given command and captures the output in the provided
    log collector.
    """

    def __init__(self, log_collector: LogCollector = None):
        self.log_collector = log_collector or LogCollector()

    def execute(
        self,
        command: typing.List[str],
        log_file_path: pathlib.Path = None,
        environ: typing.Mapping[str, str] = None,
        cwd: str = None,
        check: bool = False,
    ) -> typing.Tuple[subprocess.CompletedProcess, str]:
        name = " ".join(command)

        output_path = log_file_path or pathlib.Path(
            tempfile.NamedTemporaryFile("wt+").name
        )
        logger.debug(f"Running: {name}")
        if log_file_path:
            logger.debug(f"   -> {log_file_path}")

        # Ensure the logfile directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        run_options = {
            "stderr": subprocess.STDOUT,
            "env": (environ or os.environ),
            "universal_newlines": True,
            "check": check,
        }
        if cwd is not None:
            run_options["cwd"] = cwd

        # Write output directly to log file
        with open(output_path, "w") as fp:
            proc = subprocess.run(command, stdout=fp, **run_options)

        # Read back log file to return the output
        with open(output_path, "rt") as fp:
            output = fp.read()
            if proc.returncode:
                self.log_collector.add_failure(name, output)
                logger.error(f"Failed executing {name}")
            else:
                self.log_collector.add_success(name, output)

        return (proc, output)


class LoggingExecutor(Executor):
    """This executor executes the given command and logs it to stdout and captures the
    output in the provided log collector.
    """

    def __init__(self, log_collector: LogCollector = None):
        self.log_collector = log_collector or LogCollector()

    def execute(
        self,
        command: typing.List[str],
        log_file_path: pathlib.Path = None,
        environ: typing.Mapping[str, str] = None,
        cwd: str = None,
        check: bool = False,
    ) -> typing.Tuple[subprocess.CompletedProcess, str]:
        name = " ".join((str(arg) for arg in command))
        logger.info(f"Running: {name}")

        output_path = log_file_path or pathlib.Path(
            tempfile.NamedTemporaryFile("wt+").name
        )

        # Ensure the logfile directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Tee the output into a provided location so we can see the return the final output
        tee_proc = subprocess.Popen(["tee", output_path], stdin=subprocess.PIPE)
        run_options = {
            "stderr": subprocess.STDOUT,
            "stdout": tee_proc.stdin,
            "env": (environ or os.environ),
            "universal_newlines": True,
            "check": check,
        }
        if cwd is not None:
            run_options["cwd"] = cwd

        proc = subprocess.run(command, **run_options)

        with open(output_path, "rt") as fp:
            output = fp.read()
            if proc.returncode:
                logger.error(f"Failed executing {name}")
                self.log_collector.add_failure(name, output)
            else:
                self.log_collector.add_success(name, output)

        return (proc, output)


DEFAULT_EXECUTOR = LogCapturingExecutor()
