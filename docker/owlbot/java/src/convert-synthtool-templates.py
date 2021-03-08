# Copyright 2021 Google LLC
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

import ast
import click
from synthtool.languages import java


@click.command()
@click.option(
    "--synth-file", help="Path to synth.py file", default="synth.py",
)
def main(synth_file: str):
    excludes = []
    should_include_templates = False
    with open(synth_file, "r") as fp:
        tree = ast.parse(fp.read())

        # look for a call to java.common_templates() and extract the list of excludes
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if (
                    node.func.value.id == "java"
                    and node.func.attr == "common_templates"
                ):
                    should_include_templates = True
                    for keyword in node.keywords:
                        if keyword.arg == "excludes":
                            excludes = [element.s for element in keyword.value.elts]

    if should_include_templates:
        java.common_templates(excludes=excludes)


if __name__ == "__main__":
    main()
