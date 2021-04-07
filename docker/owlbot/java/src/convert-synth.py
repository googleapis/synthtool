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
import os
import pathlib
from typing import Union

import click
from jinja2 import Environment, FileSystemLoader


root_directory = pathlib.Path(
    os.path.realpath(os.path.dirname(os.path.realpath(__file__)))
).parent
jinja_env = Environment(
    loader=FileSystemLoader(str(root_directory / "templates")),
    keep_trailing_newline=True,
)


def load_keyword_value(tree: ast.Module, keyword: ast.keyword) -> Union[str, None]:
    if isinstance(keyword.value, ast.JoinedStr):
        # value is a f-string
        return join_string(keyword.value)
    if isinstance(keyword.value, ast.Name) and isinstance(keyword.value.ctx, ast.Load):
        return load_variable(tree, keyword.value.id)
    if isinstance(keyword.value, ast.NameConstant):
        return keyword.value.value

    print("couldn't handle keyword value")
    print(ast.dump(keyword))
    return None


def load_variable(tree: ast.Module, variable_name: str) -> Union[str, None]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and node.targets[0].id == variable_name:
            if isinstance(node.value, ast.Str):
                return node.value.s
            else:
                print("couldn't handle assignment operation")
                print(ast.dump(node.value))
                return None

    print("couldn't find variable assignment")
    return None


def join_string(joined_string: ast.JoinedStr) -> str:
    print(ast.dump(joined_string))
    joined = ""
    for value in joined_string.values:
        if isinstance(value, ast.Str):
            joined += value.s
        elif isinstance(value, ast.FormattedValue):
            joined += "{" + value.value.id + "}"
    return joined


def render(template_name: str, output_name: str, **kwargs):
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
    template_excludes = []
    should_include_templates = False
    service = None
    proto_path = None
    bazel_target = None
    destination_name = None
    cloud_api = True
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

                # look for a call to java.bazel_library() to build
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

    if proto_path:
        proto_path = proto_path.split("{version}")[0].rstrip("/")
    elif bazel_target:
        proto_path = bazel_target.split("{version}")[0].rstrip("/").lstrip("/")
    else:
        proto_path = f"google/cloud/{service}"

    artifact_name = "google-"
    if cloud_api:
        artifact_name += "cloud-"
    if destination_name:
        artifact_name += destination_name
    else:
        artifact_name += service

    render(
        template_name="owlbot.yaml.j2",
        output_name=".github/.OwlBot.yaml",
        proto_path=proto_path,
        artifact_name=artifact_name,
    )
    render(
        template_name="owlbot.py.j2",
        output_name="./owlbot.py",
        should_include_templates=should_include_templates,
        template_excludes=template_excludes,
    )
    os.remove(synth_file)


if __name__ == "__main__":
    main()
