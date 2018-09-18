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

import importlib
import os

import click

from synthtool import log


@click.command()
@click.version_option(message="%(version)s")
def main():
    synth_file = os.path.join(os.getcwd(), "synth.py")

    if os.path.lexists(synth_file):
        log.debug(f"Executing {synth_file}.")
        # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
        spec = importlib.util.spec_from_file_location("synth", synth_file)
        synth_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(synth_module)
    else:
        log.exception(f"{synth_file} not found.")
