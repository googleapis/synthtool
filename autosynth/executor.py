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
    @abstractmethod
    def execute(
        self,
        command: typing.List[str],
        log_file_path: pathlib.Path = None,
        environ: typing.Mapping[str, str] = None,
        cwd: str = None,
    ) -> typing.Tuple[subprocess.CompletedProcess, str]:
        pass

    def run(
        self,
        command: typing.List[str],
        log_file_path: pathlib.Path = None,
        environ: typing.Mapping[str, str] = None,
        cwd: str = None,
    ) -> str:
        (_, output) = self.execute(
            command, log_file_path=log_file_path, environ=environ, cwd=cwd
        )
        return output


class LogCapturingExecutor(Executor):
    def __init__(self, log_collector: LogCollector = None):
        self.log_collector = log_collector or LogCollector()

    def execute(
        self,
        command: typing.List[str],
        log_file_path: pathlib.Path = None,
        environ: typing.Mapping[str, str] = None,
        cwd: str = None,
    ) -> typing.Tuple[subprocess.CompletedProcess, str]:
        name = " ".join(command)

        output_path = log_file_path or pathlib.Path(
            tempfile.NamedTemporaryFile("wt+").name
        )
        logger.info(f"Running: {name}")
        logger.info(f"Capturing into: {output_path.name}")

        # Ensure the logfile directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        run_options = {
            "stderr": subprocess.STDOUT,
            "env": (environ or os.environ),
            "universal_newlines": True,
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
            else:
                self.log_collector.add_success(name, output)

        return (proc, output)


class LoggingExecutor(Executor):
    def __init__(self, log_collector: LogCollector = None):
        self.log_collector = log_collector or LogCollector()

    def execute(
        self,
        command: typing.List[str],
        log_file_path: pathlib.Path = None,
        environ: typing.Mapping[str, str] = None,
        cwd: str = None,
    ) -> typing.Tuple[subprocess.CompletedProcess, str]:
        name = " ".join(command)
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
        }
        if cwd is not None:
            run_options["cwd"] = cwd

        proc = subprocess.run(command, **run_options)

        with open(output_path, "rt") as fp:
            output = fp.read()
            if proc.returncode:
                self.log_collector.add_failure(name, output)
            else:
                self.log_collector.add_success(name, output)

        return (proc, output)
