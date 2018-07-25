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

import logging

try:
    from colorlog import ColoredFormatter
except ImportError:
    ColoredFormatter = None

SUCCESS = 25


class LoggerWithSuccess(logging.getLoggerClass()):  # type: ignore
    def __init__(self, name, level=logging.NOTSET):
        super(LoggerWithSuccess, self).__init__(name, level)
        logging.addLevelName(SUCCESS, "SUCCESS")

    def success(self, msg, *args, **kwargs):
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, msg, args, **kwargs)
        else:  # pragma: no cover
            pass


logging.setLoggerClass(LoggerWithSuccess)
logger = logging.getLogger("synthtool")
logger.setLevel(logging.DEBUG)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)


def success(*args, **kwargs):
    logger.success(*args, **kwargs)


def debug(*args, **kwargs):
    logger.debug(*args, **kwargs)


def info(*args, **kwargs):
    logger.info(*args, **kwargs)


def warning(*args, **kwargs):
    logger.warning(*args, **kwargs)


def error(*args, **kwargs):
    logger.warning(*args, **kwargs)


def exception(*args, **kwargs):
    logger.warning(*args, **kwargs)


def critical(*args, **kwargs):
    logger.critical(*args, **kwargs)


def _setup_logging(color: bool = bool(ColoredFormatter)):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()

    if color is True:
        formatter = ColoredFormatter(
            "%(purple)s%(name)s > %(log_color)s%(message)s",
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "blue",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_yellow",
                "SUCCESS": "green",
            },
        )

        handler.setFormatter(formatter)

    root_logger.addHandler(handler)

    # Silence any noisy loggers here.


_setup_logging()
