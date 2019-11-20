# Copyright 2019 Google LLC
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

import json
import os
import re
import yaml
from pathlib import Path
from typing import List, Dict

import requests

_RE_SAMPLE_COMMENT_START = r"\[START \w+_quickstart\w*]"
_RE_SAMPLE_COMMENT_END = r"\[END \w+_quickstart\w*]"

class Metadata:
    def __init__(self, initial_data: dict = {}):
        self._data = initial_data if initial_data else {}
        self._load_from_files()

    def _load_from_files(self) -> None:
        self._load_samples()
        self._load_partials()
        self._load_repo()

    def _load_repo(self) -> None:
        """
        loads additional meta information from .repo-metadata.json.
        """
        if os.path.exists("./.repo-metadata.json"):
            with open("./.repo-metadata.json") as f:
                self._data["repo"] = json.load(f)

    def _load_samples(self) -> None:
        """
        walks samples directory and builds up samples data-structure:

        {
            "name": "Requester Pays",
            "file": "requesterPays.js"
        }
        """
        self._data["samples"] = []
        samples_dir = Path(os.getcwd()) / "samples"
        if os.path.exists(samples_dir):
            files = os.listdir(samples_dir)
            files.sort()
            for file in files:
                if re.match(r"[\w.]+\.js$", file):
                    if file == "quickstart.js":
                        metadata["quickstart"] = self._read_quickstart(samples_dir)
                    # only add quickstart file to samples list if code sample is found.
                    if file == "quickstart.js" and not self._data.get("quickstart", None):
                        continue
                    sample_metadata = {"title": decamelize(file[:-3]), "file": file}
                    sample_metadata.update(
                        self._read_sample_metadata_comment(samples_dir, file)
                    )
                    self._data["samples"].append(sample_metadata)

    def _read_sample_metadata_comment(self, samples_dir: Path, file: str) -> Dict:
        """
        Additional meta-information can be provided through embedded comments:

        // sample-metadata:
        //   title: ACL (Access Control)
        //   description: Demonstrates setting access control rules.
        //   usage: node iam.js --help
        """
        sample_metadata = {}  # type: Dict[str, str]
        with open(samples_dir / file) as f:
            contents = f.read()
            match = re.search(
                r"(?P<metadata>// *sample-metadata:([^\n]+|\n//)+)", contents, re.DOTALL
            )
            if match:
                # the metadata yaml is stored in a comments, remove the
                # prefix so that we can parse the yaml contained.
                sample_metadata_string = re.sub(
                    r"((#|//) ?)", "", match.group("metadata")
                )
                sample_metadata = yaml.load(
                    sample_metadata_string, Loader=yaml.SafeLoader
                )["sample-metadata"]
        return sample_metadata

    def _read_quickstart(self, samples_dir: Path) -> str:
        """
        quickstart is a special case, it should be read from disk and displayed
        in README.md rather than pushed into samples array.
        """
        reading = False
        quickstart = ""

        with open(samples_dir / "quickstart.js") as f:
            while True:
                line = f.readline()
                if not line or re.search(_RE_SAMPLE_COMMENT_END, line):
                    break
                if reading:
                    quickstart += line
                if re.search(_RE_SAMPLE_COMMENT_START, line):
                    reading = True

        return quickstart

    def _load_partials(self):
        """
        hand-crafted artisinal markdown can be provided in a .readme-partials.yml.
        The following fields are currently supported:

        body: custom body to include in the usage section of the document.
        samples_body: an optional body to place below the table of contents
          in samples/README.md.
        introduction: a more thorough introduction than metadata["description"].
        title: provide markdown to use as a custom title.
        """
        cwd_path = Path(os.getcwd())
        partials_file = None
        for file in [".readme-partials.yml", ".readme-partials.yaml"]:
            if os.path.exists(cwd_path / file):
                partials_file = cwd_path / file
                break
        if not partials_file:
            return
        with open(partials_file) as f:
            self._data["partials"] = yaml.load(f, Loader=yaml.SafeLoader)

    def __getitem__(self, key: str):
        return self._data[key]


class JavaMetadata(Metadata):
    def __init__(self, initial_data: dict = {}):
        Metadata.__init__(self, initial_data)
        group_id, artifact_id = self._data["repo"]["distribution_name"].split(":")
        self._data["latestVersion"] = self._latest_artifact_version(group_id, artifact_id)
        self._data["latestBomVersion"] = self._latest_artifact_version("com.google.cloud", "libraries-bom")
        print(self._data)

    def _latest_artifact_version(self, group_id: str, artifact_id: str) -> str:
        url = "https://search.maven.org/solrsearch/select"
        params = {
            'q': f'g:{group_id} AND a:{artifact_id}',
            'start': '0',
            'rows': '20'
        }
        r = requests.get(url, params=params)
        return r.json()["response"]["docs"][0]["latestVersion"]

class NodejsMetadata(Metadata):
    def __init__(self, initial_data: dict = {}):
        Metadata.__init__(self, initial_data)
        # TODO: once we've migrated all Node.js repos to either having
        #  .repo-metadata.json, or excluding README.md, we can remove this.
        if not os.path.exists("./.repo-metadata.json"):
            self.excludes.append("README.md")
            if "samples/README.md" not in self.excludes:
                self.excludes.append("samples/README.md")

def decamelize(value: str) -> str:
    """ parser to convert fooBar.js to Foo Bar. """
    if not value:
        return ""
    str_decamelize = re.sub("^.", value[0].upper(), value)  # apple -> Apple.
    str_decamelize = re.sub(
        "([A-Z]+)([A-Z])([a-z0-9])", r"\1 \2\3", str_decamelize
    )  # ACLBatman -> ACL Batman.
    return re.sub("([a-z0-9])([A-Z])", r"\1 \2", str_decamelize)  # FooBar -> Foo Bar.