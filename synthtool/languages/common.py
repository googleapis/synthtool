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

from synthtool import transforms
import json
import os
import re

def update_library_version(version):
    """
    read package name and repository in package.json from a Node library.

    Returns:
        data - package.json file as a dict.
    """
    snippet_metadata_files = get_sample_metadata_files()
    for file in snippet_metadata_files:
        file_to_overwrite = open(file, "w")
        data = json.load(file)
        data["version"] = version
        file_to_overwrite(data)

def get_sample_metadata_files():
    rootdir = "./samples/generated"
    regex = re.compile('snipppet_metdata')

    metadata_files = []
    for root, dirs, files in os.walk(rootdir):
        for file in files:
            if regex.match(file):
                metadata_files.append[os.path.join(rootdir,file)]

    return metadata_files

