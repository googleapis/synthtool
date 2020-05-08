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

import logging


def _configure_logger():
    """Create and configure the default logger for autosynth.

    The logger will prefix the log message with the current time and the
    log severity.
    """
    logger = logging.getLogger("autosynth")
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = _configure_logger()


class LogCollector:
    def __init__(self):
        self.successes = []
        self.failures = []

    def add_success(self, name: str, log: str):
        self.successes.append((name, log))

    def add_failure(self, name: str, log: str):
        self.failures.append((name, log))
