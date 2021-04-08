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

# This script attempts to migrate simple synth.py files into owlbot
# configuration files - `owlbot.py` and `.github/.OwlBot.yaml`. It
# accomplishes this by trying to parse the `synth.py` file and detect
# the proto path and artifact names to use.

import ast
import os
import pathlib
from typing import Union
from synthtool import logger

import black
import click
from jinja2 import Environment, FileSystemLoader


# setup Jinja template path for tempated owlbot.py and .github/.OwlBot.yaml
root_directory = pathlib.Path(
    os.path.realpath(os.path.dirname(os.path.realpath(__file__)))
).parent
jinja_env = Environment(
    loader=FileSystemLoader(str(root_directory / "templates")),
    keep_trailing_newline=True,
)


def load_keyword_value(tree: ast.Module, keyword: ast.keyword) -> Union[str, None]:
    """Given a keyword argument AST node, try to grab the value.

    If the value is a variable reference, try and find a basic assignment statement.
    If the value is an f-string, return the f-string pattern.
    If the value is a string constant, return the value.

    Args:
        tree (ast.Module): The parsed source tree. Used for variable lookup.
        keyword (ast.keyword): The keyword node argument from a method call.

    Returns:
        The detected value as described above or None if we cannot parse the value.
    """
    # Handle f-strings
    if isinstance(keyword.value, ast.JoinedStr):
        return join_string(keyword.value)
    
    # Handle a simple variable reference
    if isinstance(keyword.value, ast.Name) and isinstance(keyword.value.ctx, ast.Load):
        return load_variable(tree, keyword.value.id)
    
    # Handle a string constant
    if isinstance(keyword.value, ast.NameConstant):
        return keyword.value.value

    logger.warning("couldn't handle keyword value")
    logger.debug(ast.dup(keyword))
    return None


def load_variable(tree: ast.Module, variable_name: str) -> Union[str, None]:
    """Given a variable name and the full AST tree, try to find a simple assignment
    statement that sets that variable.

    This only detects simple assignment statements like:
    `variable_name = 'some constant value'`.

    Args:
        tree (ast.Module): The parsed source tree.
        variable_name (str): The name of the variable to lookup.
    
    Returns:
        The assigned variable value if detected, otherwise None.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and node.targets[0].id == variable_name:
            if isinstance(node.value, ast.Str):
                return node.value.s
            else:
                print("couldn't handle assignment operation")
                print(ast.dump(node.value))
                return None

    logger.warning(f"couldn't find variable assignment for {variable_name}")
    return None


def join_string(joined_string: ast.JoinedStr) -> str:
    """Helper to rebuild a parsed f-string AST node into the source f-string pattern.
    
    Args:
        joined_string (ast.JoinedStr): The AST node that represents an f-string. It
            contains a list of raw strings and formatted value AST nodes.

    Returns:
        The rejoined f-string value. Example: "prefix/{var_name}/postfix"
    """
    joined = ""
    for value in joined_string.values:
        if isinstance(value, ast.Str):
            joined += value.s
        elif isinstance(value, ast.FormattedValue):
            joined += "{" + value.value.id + "}"
    return joined


def render(template_name: str, output_name: str, **kwargs) -> None:
    """Helper to generate a file from a template.

    Args:
        template_name (str): The name of the template file.
        output_name (str): The name of the output file. Can be an
            absolute or relative path.
    
    Returns:
        None
    """
    template = jinja_env.get_template(template_name)
    t = template.stream(kwargs)
    directory = os.path.dirname(output_name)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    t.dump(str(output_name))


@click.command()
@click.option(
    "--synth-file", help="Path to synth.py file", default="synth.py",
)
def main(synth_file: str):
    if not os.path.isfile(synth_file):
        logger.error(f"failed to find: {synth_file}")
        return

    template_excludes = []
    should_include_templates = False
    service = None
    proto_path = None
    bazel_target = None
    destination_name = None
    cloud_api = True
    found_replacement = False
    with open(synth_file, "r") as fp:
        tree = ast.parse(fp.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # look for a call to java.common_templates() and extract the list of excludes
                if (
                    node.func.value.id == "java"
                    and node.func.attr == "common_templates"
                ):
                    should_include_templates = True
                    for keyword in node.keywords:
                        if keyword.arg == "excludes":
                            template_excludes = [
                                element.s for element in keyword.value.elts
                            ]

                # look for a call to java.bazel_library() to extra key attributes
                if node.func.value.id == "java" and node.func.attr == "bazel_library":
                    for keyword in node.keywords:
                        if keyword.arg == "service":
                            service = load_keyword_value(tree, keyword)
                        if keyword.arg == "proto_path":
                            proto_path = load_keyword_value(tree, keyword)
                        if keyword.arg == "bazel_target":
                            bazel_target = load_keyword_value(tree, keyword)
                        if keyword.arg == "destination_name":
                            destination_name = load_keyword_value(tree, keyword)
                        if keyword.arg == "cloud_api":
                            cloud_api = load_keyword_value(tree, keyword)

                # look for a call to java.pregenerated_library() to extra key attributes
                if (
                    node.func.value.id == "java"
                    and node.func.attr == "pregenerated_library"
                ):
                    for keyword in node.keywords:
                        if keyword.arg == "service":
                            service = load_keyword_value(tree, keyword)
                        if keyword.arg == "path":
                            proto_path = load_keyword_value(tree, keyword)
                        if keyword.arg == "destination_name":
                            destination_name = load_keyword_value(tree, keyword)
                        if keyword.arg == "cloud_api":
                            cloud_api = load_keyword_value(tree, keyword)

                # look for a call to synthtool.replace()
                if node.func.attr == "replace":
                    found_replacement = True

    # If the synth.py includes replacements, don't try to migrate
    if found_replacement:
        logger.error(f"{synth_file} includes replacements -- aborting")
        return

    if proto_path:
        proto_path = proto_path.split("{version}")[0].rstrip("/")
    elif bazel_target:
        proto_path = bazel_target.split("{version}")[0].rstrip("/").lstrip("/")
    else:
        proto_path = "google/cloud/{service}"
    proto_path = proto_path.format(service=service)

    artifact_name = "google-"
    if cloud_api:
        artifact_name += "cloud-"
    if destination_name:
        artifact_name += destination_name
    else:
        artifact_name += service

    logger.info("writing .github.OwlBot.yaml")
    logger.debug(f"proto_path: {proto_path}")
    logger.debug(f"artifact_name: {artifact_name}")
    render(
        template_name="owlbot.yaml.j2",
        output_name=".github/.OwlBot.yaml",
        proto_path=proto_path,
        artifact_name=artifact_name,
    )
    logger.info("writing owlbot.py")
    logger.debug(f"should_include_templates: {should_include_templates}")
    logger.debug(f"template_excludes: {template_excludes}")
    render(
        template_name="owlbot.py.j2",
        output_name="./owlbot.py",
        should_include_templates=should_include_templates,
        template_excludes=template_excludes,
    )
    logger.info("reformatting owlbot.py")
    black.reformat_one(
        src=pathlib.Path("./owlbot.py"),
        fast=True,
        write_back=black.WriteBack.YES,
        mode=black.FileMode(),
        report=black.Report(),
    )
    logger.info(f"removing {synth_file}")
    os.remove(synth_file)


if __name__ == "__main__":
    main()
