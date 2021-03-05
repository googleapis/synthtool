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
import json
import os
from typing import Mapping
from poms import module, templates


def load_versions(filename: str, default_group_id: str) -> Mapping[str, module.Module]:
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
            version="0.0.1-SNAPSHOT",
            release_version="0.0.0",
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
    modules = [main_module] + proto_modules + grpc_modules

    if not os.path.isfile(f"{artifact_id}/pom.xml"):
        print(f"creating missing cloud pom.xml")
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

    if not os.path.isfile(f"{artifact_id}-bom/pom.xml"):
        print(f"creating missing bom pom.xml")
        templates.render(
            template_name="bom_pom.xml.j2",
            output_name=f"{artifact_id}-bom/pom.xml",
            repo=repo_metadata["repo"],
            name=name,
            modules=modules,
            main_module=main_module,
        )

    if not os.path.isfile("pom.xml"):
        print("creating missing parent pom.xml")
        templates.render(
            template_name="parent_pom.xml.j2",
            output_name="./pom.xml",
            repo=repo_metadata["repo"],
            modules=modules,
            main_module=main_module,
            name=name,
        )

    if not os.path.isfile("versions.txt"):
        print("creating missing versions.txt")
        templates.render(
            template_name="versions.txt.j2",
            output_name="./versions.txt",
            modules=modules,
        )


if __name__ == "__main__":
    main()
