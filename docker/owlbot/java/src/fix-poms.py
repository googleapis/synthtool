# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import glob
import inspect
import itertools
import json
from lxml import etree
import os
import re
from typing import List, Mapping
from poms import module, templates


def load_versions(filename: str, default_group_id: str) -> Mapping[str, module.Module]:
    if not os.path.isfile(filename):
        return {}
    modules = {}
    with open(filename, "r") as fp:
        for line in fp:
            line = line.strip()
            if line.startswith("#"):
                continue

            parts = line.split(":")
            if len(parts) == 3:
                artifact_id = parts[0]
                group_id = (
                    default_group_id
                    if artifact_id.startswith("google-")
                    else "com.google.api.grpc"
                )
                modules[artifact_id] = module.Module(
                    group_id=group_id,
                    artifact_id=artifact_id,
                    release_version=parts[1],
                    version=parts[2],
                )

    return modules


def _find_dependency_index(dependencies, group_id, artifact_id) -> int:
    try:
        return next(
            i
            for i, x in enumerate(dependencies.getchildren())
            if _dependency_matches(x, group_id, artifact_id)
        )
    except StopIteration:
        return -1


def _dependency_matches(node, group_id, artifact_id) -> bool:
    artifact_node = node.find("{http://maven.apache.org/POM/4.0.0}artifactId")
    group_node = node.find("{http://maven.apache.org/POM/4.0.0}groupId")

    if artifact_node is None or group_node is None:
        return False

    return artifact_node.text.startswith(artifact_id) and group_node.text.startswith(
        group_id
    )


def _is_cloud_client(proto_modules: List[module.Module], grpc_modules: List[module.Module]) -> bool:
    return len(proto_modules) > 0 or len(grpc_modules) > 0


def update_cloud_pom(
    filename: str, proto_modules: List[module.Module], grpc_modules: List[module.Module]
):
    tree = etree.parse(filename)
    root = tree.getroot()
    dependencies = root.find("{http://maven.apache.org/POM/4.0.0}dependencies")

    existing_dependencies = [
        m.find("{http://maven.apache.org/POM/4.0.0}artifactId").text
        for m in dependencies
        if m.find("{http://maven.apache.org/POM/4.0.0}artifactId") is not None
    ]

    try:
        grpc_index = _find_dependency_index(
            dependencies, "com.google.api.grpc", "grpc-"
        )
    except StopIteration:
        grpc_index = _find_dependency_index(dependencies, "junit", "junit")
    # insert grpc dependencies after junit
    for m in grpc_modules:
        if m.artifact_id not in existing_dependencies:
            print(f"adding new test dependency {m.artifact_id}")
            new_dependency = etree.Element(
                "{http://maven.apache.org/POM/4.0.0}dependency"
            )
            new_dependency.tail = "\n    "
            new_dependency.text = "\n      "
            new_group = etree.Element("{http://maven.apache.org/POM/4.0.0}groupId")
            new_group.text = m.group_id
            new_group.tail = "\n      "
            new_artifact = etree.Element(
                "{http://maven.apache.org/POM/4.0.0}artifactId"
            )
            new_artifact.text = m.artifact_id
            new_artifact.tail = "\n      "
            new_scope = etree.Element("{http://maven.apache.org/POM/4.0.0}scope")
            new_scope.text = "test"
            new_scope.tail = "\n    "
            new_dependency.append(new_group)
            new_dependency.append(new_artifact)
            new_dependency.append(new_scope)
            dependencies.insert(grpc_index + 1, new_dependency)

    try:
        proto_index = _find_dependency_index(
            dependencies, "com.google.api.grpc", "proto-"
        )
    except StopIteration:
        print("after protobuf")
        proto_index = _find_dependency_index(
            dependencies, "com.google.protobuf", "protobuf-java"
        )
    # insert proto dependencies after protobuf-java
    for m in proto_modules:
        if m.artifact_id not in existing_dependencies:
            if re.match(r"proto-.*-v\d+.*", m.artifact_id):
                print(f"adding new dependency {m.artifact_id}")
                new_dependency = etree.Element(
                    "{http://maven.apache.org/POM/4.0.0}dependency"
                )
                new_dependency.tail = "\n    "
                new_dependency.text = "\n      "
                new_group = etree.Element("{http://maven.apache.org/POM/4.0.0}groupId")
                new_group.text = m.group_id
                new_group.tail = "\n      "
                new_artifact = etree.Element(
                    "{http://maven.apache.org/POM/4.0.0}artifactId"
                )
                new_artifact.text = m.artifact_id
                new_artifact.tail = "\n    "
                new_dependency.append(new_group)
                new_dependency.append(new_artifact)
                dependencies.insert(proto_index + 1, new_dependency)

    tree.write(filename, pretty_print=True, xml_declaration=True, encoding="utf-8")


def update_parent_pom(filename: str, modules: List[module.Module]):
    tree = etree.parse(filename)
    root = tree.getroot()

    # BEGIN: update modules
    existing = root.find("{http://maven.apache.org/POM/4.0.0}modules")

    module_names = [m.artifact_id for m in modules]
    extra_modules = [
        m.text for i, m in enumerate(existing) if m.text not in module_names
    ]

    modules_to_write = module_names + extra_modules
    num_modules = len(modules_to_write)

    existing.clear()
    existing.text = "\n    "
    for index, m in enumerate(modules_to_write):
        new_module = etree.Element("{http://maven.apache.org/POM/4.0.0}module")
        new_module.text = m
        if index == num_modules - 1:
            new_module.tail = "\n  "
        else:
            new_module.tail = "\n    "
        existing.append(new_module)

    existing.tail = "\n\n  "
    # END: update modules

    # BEGIN: update versions in dependencyManagement
    dependencies = root.find(
        "{http://maven.apache.org/POM/4.0.0}dependencyManagement"
    ).find("{http://maven.apache.org/POM/4.0.0}dependencies")

    existing_dependencies = [
        m.find("{http://maven.apache.org/POM/4.0.0}artifactId").text
        for m in dependencies
        if m.find("{http://maven.apache.org/POM/4.0.0}artifactId") is not None
    ]
    insert_index = 1

    num_modules = len(modules)

    for index, m in enumerate(modules):
        if m.artifact_id in existing_dependencies:
            continue

        new_dependency = etree.Element("{http://maven.apache.org/POM/4.0.0}dependency")
        new_dependency.tail = "\n      "
        new_dependency.text = "\n        "
        new_group = etree.Element("{http://maven.apache.org/POM/4.0.0}groupId")
        new_group.text = m.group_id
        new_group.tail = "\n        "
        new_artifact = etree.Element("{http://maven.apache.org/POM/4.0.0}artifactId")
        new_artifact.text = m.artifact_id
        new_artifact.tail = "\n        "
        new_version = etree.Element("{http://maven.apache.org/POM/4.0.0}version")
        new_version.text = m.version
        comment = etree.Comment(" {x-version-update:" + m.artifact_id + ":current} ")
        comment.tail = "\n      "
        new_dependency.append(new_group)
        new_dependency.append(new_artifact)
        new_dependency.append(new_version)
        new_dependency.append(comment)
        new_dependency.tail = "\n      "
        dependencies.insert(1, new_dependency)

    # END: update versions in dependencyManagement

    tree.write(filename, pretty_print=True, xml_declaration=True, encoding="utf-8")


def update_bom_pom(filename: str, modules: List[module.Module]):
    tree = etree.parse(filename)
    root = tree.getroot()
    existing = root.find(
        "{http://maven.apache.org/POM/4.0.0}dependencyManagement"
    ).find("{http://maven.apache.org/POM/4.0.0}dependencies")

    num_modules = len(modules)

    existing.clear()
    existing.text = "\n      "
    for index, m in enumerate(modules):
        new_dependency = etree.Element("{http://maven.apache.org/POM/4.0.0}dependency")
        new_dependency.tail = "\n      "
        new_dependency.text = "\n        "
        new_group = etree.Element("{http://maven.apache.org/POM/4.0.0}groupId")
        new_group.text = m.group_id
        new_group.tail = "\n        "
        new_artifact = etree.Element("{http://maven.apache.org/POM/4.0.0}artifactId")
        new_artifact.text = m.artifact_id
        new_artifact.tail = "\n        "
        new_version = etree.Element("{http://maven.apache.org/POM/4.0.0}version")
        new_version.text = m.version
        comment = etree.Comment(" {x-version-update:" + m.artifact_id + ":current} ")
        comment.tail = "\n      "
        new_dependency.append(new_group)
        new_dependency.append(new_artifact)
        new_dependency.append(new_version)
        new_dependency.append(comment)

        if index == num_modules - 1:
            new_dependency.tail = "\n    "
        else:
            new_dependency.tail = "\n      "
        existing.append(new_dependency)

    existing.tail = "\n  "

    tree.write(filename, pretty_print=True, xml_declaration=True, encoding="utf-8")


def main():
    with open(".repo-metadata.json", "r") as fp:
        repo_metadata = json.load(fp)

    group_id, artifact_id = repo_metadata["distribution_name"].split(":")
    name = repo_metadata["name_pretty"]

    existing_modules = load_versions("versions.txt", group_id)

    if artifact_id not in existing_modules:
        existing_modules[artifact_id] = module.Module(
            group_id=group_id,
            artifact_id=artifact_id,
            version="0.0.1-SNAPSHOT",
            release_version="0.0.0",
        )
    main_module = existing_modules[artifact_id]

    parent_artifact_id = f"{artifact_id}-parent"
    if parent_artifact_id not in existing_modules:
        existing_modules[parent_artifact_id] = module.Module(
            group_id=group_id,
            artifact_id=parent_artifact_id,
            version=main_module.version,
            release_version=main_module.release_version,
        )
    parent_module = existing_modules[parent_artifact_id]

    for path in glob.glob("proto-google-*"):
        if not path in existing_modules:
            existing_modules[path] = module.Module(
                group_id="com.google.api.grpc",
                artifact_id=path,
                version=main_module.version,
                release_version=main_module.release_version,
            )

        if not os.path.isfile(f"{path}/pom.xml"):
            print(f"creating missing proto pom: {path}")
            templates.render(
                template_name="proto_pom.xml.j2",
                output_name=f"{path}/pom.xml",
                module=existing_modules[path],
                parent_module=parent_module,
                main_module=main_module,
            )

    for path in glob.glob("grpc-google-*"):
        if not path in existing_modules:
            existing_modules[path] = module.Module(
                group_id="com.google.api.grpc",
                artifact_id=path,
                version=main_module.version,
                release_version=main_module.release_version,
            )

        if not os.path.isfile(f"{path}/pom.xml"):
            proto_artifact_id = path.replace("grpc-", "proto-")
            print(f"creating missing grpc pom: {path}")
            templates.render(
                template_name="grpc_pom.xml.j2",
                output_name=f"{path}/pom.xml",
                module=existing_modules[path],
                parent_module=parent_module,
                main_module=main_module,
                proto_module=existing_modules[proto_artifact_id],
            )
    proto_modules = [
        module
        for module in existing_modules.values()
        if module.artifact_id.startswith("proto-")
    ]
    grpc_modules = [
        module
        for module in existing_modules.values()
        if module.artifact_id.startswith("grpc-")
    ]
    modules = [main_module] + grpc_modules + proto_modules

    if not _is_cloud_client(proto_modules, grpc_modules):
        print("no proto or grpc modules - probably not a cloud client")
        return

    if os.path.isfile(f"{artifact_id}/pom.xml"):
        print("updating modules in cloud pom.xml")
        update_cloud_pom(f"{artifact_id}/pom.xml", proto_modules, grpc_modules)
    else:
        print("creating missing cloud pom.xml")
        templates.render(
            template_name="cloud_pom.xml.j2",
            output_name=f"{artifact_id}/pom.xml",
            module=main_module,
            parent_module=parent_module,
            repo=repo_metadata["repo"],
            name=name,
            description=repo_metadata["api_description"],
            proto_modules=proto_modules,
            grpc_modules=grpc_modules,
        )

    if os.path.isfile(f"{artifact_id}-bom/pom.xml"):
        print("updating modules in bom pom.xml")
        update_bom_pom(f"{artifact_id}-bom/pom.xml", modules)
    else:
        print("creating missing bom pom.xml")
        templates.render(
            template_name="bom_pom.xml.j2",
            output_name=f"{artifact_id}-bom/pom.xml",
            repo=repo_metadata["repo"],
            name=name,
            modules=modules,
            main_module=main_module,
        )

    if os.path.isfile("pom.xml"):
        print("updating modules in parent pom.xml")
        update_parent_pom("pom.xml", modules)
    else:
        print("creating missing parent pom.xml")
        templates.render(
            template_name="parent_pom.xml.j2",
            output_name="./pom.xml",
            repo=repo_metadata["repo"],
            modules=modules,
            main_module=main_module,
            name=name,
        )

    if os.path.isfile("versions.txt"):
        print("updating modules in versions.txt")
    else:
        print("creating missing versions.txt")
    templates.render(
        template_name="versions.txt.j2", output_name="./versions.txt", modules=modules,
    )


if __name__ == "__main__":
    main()
